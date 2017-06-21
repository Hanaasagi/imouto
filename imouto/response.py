import json
from collections import Mapping
from http.cookies import SimpleCookie
from imouto.util import HeaderDict, tob, touni
from http.client import responses as ALL_STATUS


class Response:

    def __init__(self, version='1.1', status_code=200):
        self.version = version
        self.status_code = status_code
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

    def output(self):
        if 'Content-Length' not in self.headers:
            self.headers['Content-Length'] = touni(sum(len(_) for _ in self._chunks))

        headers = b''.join(b'%b: %b\r\n' % (tob(key), tob(value)) for key, value in self.headers.items())

        if self.cookies:
            headers += tob(self.cookies.output()) + b'\r\n'
        status = ALL_STATUS.get(self.status_code)
        return (b'HTTP/%b %d %b\r\n'
                b'%b\r\n'
                b'%b' % (
                    tob(self.version),
                    self.status_code,
                    tob(status),
                    headers,
                    b''.join(self._chunks),
                ))
