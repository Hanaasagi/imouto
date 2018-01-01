"""
implement exceptions
"""

from http import HTTPStatus


class ConfigError(Exception):
    """"""


class HTTPError(Exception):
    """ Exception represented HTTP Error """

    _status_code = 500
    _phrase = 'Internal Server Error'

    def __init__(self, status_code: int = None, log_message: str = '') -> None:
        self._status_code: int = status_code or self._status_code
        self.log_message: str = log_message
        message = '[status {}] {}'.format(self.status_code,
                                          self.log_message or self._phrase)
        super().__init__(message)

    @property
    def status_code(self):
        return self._status_code

    @property
    def phrase(self):
        return self._phrase


for status_obj in list(HTTPStatus):
    status_code = status_obj.value
    if status_code > 400:
        class_name = status_obj.name.title().replace('_', '')
        attrs = {
            '_status_code': status_code,
            '_phrase': status_obj.name.replace('_', ' ')
        }
        cls = type(class_name, (HTTPError,), attrs)
        globals()[class_name] = cls
