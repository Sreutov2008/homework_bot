class GetAPIException(Exception):
    """При сбое запроса к API."""


class NoDocumentException(Exception):
    """Прри неизвестном статусе домашки."""


class MissingKeyException(Exception):
    """При отсутствии ключей в ответе API."""
