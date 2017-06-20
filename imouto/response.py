import json
from collections import Mapping
from http.cookies import SimpleCookie
from imouto.util import HeaderDict, tob


class Response:

    def __init__(self):
        self.status_code = 200
        self._chunks = []
        self.headers = HeaderDict([
            ('Content-Type', 'text/html')
        ])
        self.cookies = SimpleCookie()

    def clear(self):
        self._chunks = []

    def write(self, str_):
        self._chunks.append(tob(str_))

    def write_bytes(self, bytes_):
        self._chunks.append(bytes_)

    def write_json(self, data):
        if issubclass(type(data), Mapping):
            data_str = json.dumps(data)
        elif hasattr(data, '_asdict'):
            data_str = json.dumps(data._asdict())
        else:
            raise TypeError("Must to dict-like type")
        self.headers['Content-Type'] = 'application/json'
        self._chunks.append(tob(data_str))
