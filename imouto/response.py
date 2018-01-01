import time
import json
from collections import Mapping
from http.cookies import SimpleCookie
from imouto.datastructures import HeaderDict
from datetime import date as date_t, datetime, timedelta
from http.client import responses as ALL_STATUS
from imouto.utils import tob, touni, hkey, hval


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

    def set_cookie(self, name: str, value: str, **options):
        """ set cookie to http resposne
        :param options: enable to include following options
        :param max_age: maximum age in seconds. (default: None)
        :param expires: a datetime object or UNIX timestamp. (default: None)
        :param domain: the domain that is allowed to read the cookie.
            (default: current domain)
        :param path: limits the cookie to a given path (default: current path)
        :param secure: limit the cookie to HTTPS connections (default: off).
        :param httponly: prevents client-side javascript to read this cookie
            (default: off, requires Python 2.6 or newer).
        """
        if len(value) > 4096:
            raise ValueError('cookie value is too long.')

        self.cookies[name.strip()] = hval(value)

        for key, value in options.items():
            key = hkey(key)
            if key == 'max_age':
                if isinstance(value, timedelta):
                    value = value.seconds + value.days * 24 * 3600
            if key == 'expires':
                if isinstance(value, (date_t, datetime)):
                    value = value.timetuple()
                elif isinstance(value, (int, float)):
                    value = time.gmtime(value)
                assert isinstance(value, tuple)
                value = time.strftime("%a, %d %b %Y %H:%M:%S GMT", value)
            self.cookies[name][key] = value

    def clear_cookie(self, key: str, **options):
        """ make the cookie expired
        IE6, IE7, and IE8 does not support “max-age”, while (mostly)
        all browsers support expires
        """
        options['max_age'] = -1
        options['expires'] = 0
        self.set_cookie(key, '', **options)

    def output(self):
        if 'Content-Length' not in self.headers:
            self.headers['Content-Length'] = touni(sum(len(_)
                                                       for _ in self._chunks))

        headers = b''.join(b'%b: %b\r\n' % (tob(key), tob(value))
                           for key, value in self.headers.items())

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
