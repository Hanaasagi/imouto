import io
import json
import cgi
import urllib.parse as parse
from httptools import parse_url
from imouto.httputils import MultiDict, HeaderDict


REQUEST_STATE_PROCESSING = 0
REQUEST_STATE_CONTINUE = 1
REQUEST_STATE_COMPLETE = 2


class FileStorage:

    def __init__(self, field_storage):
        self.filename = field_storage.filename
        self.value = field_storage.value


class Request:

    def __init__(self, method=None, path=None, query_string='',
                 args=None, headers=None, form=None, cookies=None):
        self._header_list = []
        self._state = REQUEST_STATE_PROCESSING
        self.method = method
        self.path = path
        self.query_string = query_string
        self.query = None
        self.args = args
        self.headers = HeaderDict()
        self.cookies = MultiDict()
        self.raw_body = io.BytesIO()
        self.form = form

        if query_string:
            self.query = MultiDict(parse.parse_qs(self.query_string))

        if headers:
            self.headers = HeaderDict(**headers)

        if cookies:
            self.cookies = MultiDict(**cookies)

    def _parse_cookie(self, value):
        cookies = trim_keys(parse.parse_qs(value))
        return MultiDict(cookies)

    def _parse_form(self, body_stream):
        env = {'REQUEST_METHOD': 'POST'}
        form = cgi.FieldStorage(body_stream, headers=self.headers, environ=env)
        d = {}
        for k in form.keys():
            if form[k].filename:
                d[k] = [FileStorage(form[k])]
            else:
                d[k] = [form[k].value]
        return MultiDict(d)

    def _parse_body(self, body_stream):
        content_type = self.headers.get('Content-Type', '')
        if content_type == 'application/json':
            data = body_stream.getvalue().decode()
            self.form = json.loads(data)
        elif content_type.startswith('multipart/form-data'):
            self.form = self._parse_form(body_stream)
        elif content_type == 'application/x-www-form-urlencoded':
            data = body_stream.getvalue().decode()
            self.form = MultiDict(parse.parse_qs(data))

        body_stream.seek(0)

    def on_url(self, url: bytes):
        parsed = parse_url(url)
        self.path = parsed.path.decode()
        self.query_string = (parsed.query or b'').decode()
        self.query = MultiDict(parse.parse_qs(self.query_string))

    def on_header(self, name: bytes, value: bytes):
        self._header_list.append((name.decode(), value.decode()))
        if name.lower() == b'except' and value == b'100-continue':
            self._state = REQUEST_STATE_CONTINUE

    def on_headers_complete(self):
        self.headers = HeaderDict(self._header_list)
        cookie_value = self.headers.get('Cookie')
        if cookie_value:
            self.cookies = self._parse_cookie(cookie_value)

    def on_body(self, body: bytes):
        self.raw_body.write(body)

    def on_message_complete(self):
        self._state = REQUEST_STATE_COMPLETE
        self.raw_body.seek(0)
        self._parse_body(self.raw_body)

    @property
    def finished(self):
        return self._state == REQUEST_STATE_COMPLETE

    @property
    def needs_write_continue(self):
        return self._state == REQUEST_STATE_CONTINUE

    def reset_state(self):
        self._state = REQUEST_STATE_PROCESSING
