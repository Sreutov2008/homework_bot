import os
from dotenv import load_dotenv
import telebot

load_dotenv()

TELEGRAM_TOKEN_FITCOM = os.getenv("TELEGRAM_TOKEN_FITCOM")
weight = 0
waist_circumference = 0


bot = telebot.TeleBot(token=TELEGRAM_TOKEN_FITCOM)


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    #user_markup.row('Посчитай жир')
    bot.send_message(message.chat.id,
                     'Добро пожаловать..',
                     reply_markup=user_markup
                     )

@bot.message_handler(commands=['stop'])
def handle_start(message):
    hide_markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, '..', reply_markup=hide_markup)



@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Привет':
        bot.send_message(message.chat.id, "Привет, как ты?")
    
    if message.text == '/fats' or '/fats@Fitcom_bot':
        bot.send_message(message.chat.id, "Введите свой вес: ")
        bot.register_next_step_handler(message, get_weight)


def get_weight(message):
    """Функция захвата веса."""
    global weight
    try:
        weight = float(message.text)    
        bot.send_message(message.chat.id, 'Введите окружность талии:')
        bot.register_next_step_handler(message, get_waist_circumference)
    except Exception:
        bot.send_message(message.chat.id,
                        f'Давай заново, укажи вес цифрами.'
                        f'Напиши в чат "Посчитай жир" или выбери в меню "/fats"'
                        )


def get_waist_circumference(message):
    """Фукция захвата окружности талии и расчета параметров."""
    global waist_circumference
    try:
        waist_circumference = float(message.text)
        fat_percentage = ((((4.15 * waist_circumference) / 2.54 -
                     (0.082 * weight) / 0.454 - 76.76)) / (weight / 0.454)) * 100

        weight_no_fat = weight - (fat_percentage * weight) / 100
        bot.send_message(message.chat.id,
                        f'Процент жира в вашем теле {fat_percentage: .1f}%\n'
                        f'Масса тела без жира {weight_no_fat: .1f}кг'
                        )
        bot.send_message(message.chat.id,
                        f'Белка нужно {weight_no_fat*3.3: .0f} г\n'
                        f'Углеводов нужно {weight_no_fat*2.2: .0f} г\n'
                        f'Жира нужно {weight_no_fat*1.1: .0f} г'
                        )
    except Exception:
        bot.send_message(message.chat.id,
                        f'Давай заново, укажи окружность талии цифрами.'
                        f'Напиши в чат "Посчитай жир" или выбери в меню "/fats"'
                        )


bot.polling(non_stop=True, interval=0)
