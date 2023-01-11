import os
from dotenv import load_dotenv
import logging
import requests
import telegram
import time
import sys
from exceptions import GetAPIException, NoDocumentException, MissingKeyException

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

homeworks_dict = {}
error_dict = {}



HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s  %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.ERROR
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



def check_tokens():
    '''Проверка переменных окружения'''
    no_token_message = (
        'Бот принудительно остановлен.'
        'Отсутствует обязательная переменная окружения:'
    )
    token_bool = True
    if PRACTICUM_TOKEN is None:
        token_bool = False
        logger.critical(f'{no_token_message} PRACTICUM_TOKEN')
    if TELEGRAM_TOKEN is None:
        token_bool = False
        logger.critical(f'{no_token_message} TELEGRAM_TOKEN')
    if TELEGRAM_CHAT_ID is None:
        token_bool = False
        logger.critical(f'{no_token_message} TELEGRAM_CHAT_ID')
    return token_bool
    


def send_message(bot, message):
    '''Отправка сообщений в телеграмм'''
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Сообщение улетело')
    except Exception as error:
        logger.error(f'Сбой при отправки сообщения: {error}')


def get_api_answer(timestamp):
    '''Запрос информации от API Я.Практикум'''
    payload = {'from_date': timestamp}
    homework_statuses_json = dict()
    try:
        homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        homework_statuses_json = homework_statuses.json()
        if homework_statuses.status_code != 200:
            raise GetAPIException
        logger.debug('Получен запрос от API и обработан в json')
        return homework_statuses_json
    except Exception:
        if homework_statuses.status_code != 200:
            raise GetAPIException('Эндпоинт API недоступен')
        else:
            raise GetAPIException('Сбой при запросе к эндпоинту')


def check_response(response):
    """Проверяем информацию запрошенную от API"""
    try:
        homeworks = response['homeworks']
        last_current_date = response['current_date']
    except KeyError:
        raise MissingKeyException(
            'Отсутствуют ожидаемые ключи в ответе API'
        )
    if not isinstance(response, dict):
        raise TypeError("Некорректный тип у response.")
   
    if not isinstance(homeworks, list):
        raise TypeError("Некорректный тип у homeworks.")
    if homeworks != []:
        
       
        homeworks_dict['last_homework'] = homeworks[0]
        homeworks_dict['last_timestamp'] = last_current_date
        logger.debug(
            'Обновление информации в словаре о последней проверке'
        )
        logger.debug(
            'Домашня работа проверена за время этой итеррации'
        )
        return True
    else:
        logger.debug(
            'Домашня работа не проверена за время этой итеррации'
        )
        return False


def parse_status(homework):
    """Проверка статуса домашней работы."""
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise Exception('Домашняя работа без имени')
    status = homework.get('status')
    if status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS[status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        raise NoDocumentException('Недокументированый статус домашней работы')


def main():
    """Основная логика работы бота."""
    logger.debug('-----------------')
    if not check_tokens():
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    send_message(bot, 'Работа начата')
    while True:
        try:
            if homeworks_dict.get('last_timestamp'):
                timestamp = homeworks_dict.get('last_timestamp')
            response = get_api_answer(timestamp)
            homework_status_changed = check_response(response)
            if homework_status_changed:
                last_homework = homeworks_dict.get('last_homework')
                message = parse_status(last_homework)
                send_message(bot, message)
            logger.debug('-----------------')
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}')
            message = f'Сбой в работе программы: {error}'
            if message != error_dict.get('last_error_message'):
                error_dict['last_error_message'] = message
                send_message(bot, message)
            logger.debug('-----------------')
            time.sleep(RETRY_PERIOD)
            


if __name__ == '__main__':
    main()
