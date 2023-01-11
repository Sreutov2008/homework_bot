class GetAPIException(Exception):
    """Своё исклюение при сбое запроса к API """

class NoDocumentException(Exception):
    """Своё исключение при неизвестном статусе домашки"""

class MissingKeyException(Exception):
    """Своё исключение при отсутствии клюей в ответе API"""


