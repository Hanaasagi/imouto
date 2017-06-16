import json
from http.cookies import SimpleCookie
from imouto.httputils import HeaderDict


class Response:

    def __init__(self):
        self.status_code = 200
        self._chunks = []
        self.headers = HeaderDict([
            ('Content-Type', 'text/html')
        ])
        self.cookies = SimpleCookie()

    def _clear(self):
        self._chunks = []

    def _write(self, string):
        self._chunks.append(string.encode())

    def _write_bytes(self, bytes_):
        self._chunks.append(bytes_)

    def _write_json(self, data):
        self.headers['Content-Type'] = 'application/json'
        self._chunks.append(json.dumps(data).encode())
