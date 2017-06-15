import json
from imouto.httputils import HeaderDict


class Response:

    def __init__(self):
        self.status_code = 200
        self._chunks = []
        self.headers = HeaderDict([
            ('Content-Type', 'text/html')
        ])
        self.cookies = {}

    def clear(self):
        self._chunks = []

    def write(self, string):
        self._chunks.append(string.encode())

    def write_bytes(self, bytes):
        self._chunks.append(bytes)

    def write_json(self, data):
        self.headers['Content-Type'] = 'application/json'
        self._chunks.append(json.dumps(data).encode())
