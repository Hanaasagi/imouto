import re
import asyncio
import traceback
from datetime import datetime
from imouto import Request, Response
from imouto.autoload import autoload
from http.client import responses as http_status
from httptools import HttpRequestParser


# `uvloop` can improve performance significantly
# import uvloop
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class HTTPError(Exception):
    """
    """

    def __init__(self, status_code=500, log_message=None, *args):
        self.status_code = status_code
        self.log_message = log_message
        self.args = args
        if log_message and not args:
            self.log_message = log_message.replace('%', '%%')

    def __str__(self):
        message = "HTTP %d: %s" % (self.status_code,
                                   http_status.get(self.status_code, 'Unknown'))
        if self.log_message:
            return message + " (" + (self.log_message % self.args) + ")"
        else:
            return message


class RequestHandler:
    """Base class
    """

    def __init__(self, application, request, response, **kwargs):
        """subclass should override initialize method rather than this
        """
        self.application = application
        self.request = request
        self.response = response
        self.initialize(**kwargs)

    def initialize(self):
        """subclass initialization
        """
        pass

    async def prepare(self):
        """invoked before get/post/
        """
        pass

    async def head(self, *args, **kwargs):
        raise HTTPError(405)

    async def get(self, *args, **kwargs):
        raise HTTPError(405)

    async def post(self, *args, **kwargs):
        raise HTTPError(405)

    async def delete(self, *args, **kwargs):
        raise HTTPError(405)

    async def patch(self, *args, **kwargs):
        raise HTTPError(405)

    async def put(self, *args, **kwargs):
        raise HTTPError(405)

    async def options(self, *args, **kwargs):
        raise HTTPError(405)

    async def redirect(self, url, permanent=False):
        if permanent:
            self.response.status_code = status_codes.HTTP_301
        else:
            self.response.status_code = status_codes.HTTP_302
        self.response.headers['Location'] = url

    async def write_cookie(self, writer, key, value):
        if isinstance(value, tuple):
            value, duration = value
            if isinstance(duration, datetime):
                format = duration.strftime('%a %d %b %Y %H:%M:%S GMT').encode()
                writer.write(b'Set-Cookie: %s-%s;expires=%s\r\n' % (
                    key.encode(), str(value).encode(), format))
            elif isinstance(duration, int):
                writer.write(b'Set-Cookie: %s=%s;max-age=%d\r\n' % (
                    key.encode(), str(value).encode(), duration))
        else:
            writer.write(b'Set-Cookie: %s=%s\r\n' % (
                key.encode(), str(value).encode()))


class RedirectHandler(RequestHandler):

    def initialize(self, url, permanent=True):
        self._url = url
        self._permanent = permanent

    async def get(self):
        self.redirect(self._url, permanent=self._permanent)


class ErrorHandler(RequestHandler):
    pass


class Application:

    def __init__(self, handlers=None, **settings):
        self._handlers = []
        self.settings = settings

        if handlers:
            self.add_handlers(handlers)

    def add_handlers(self, handlers):
        """Append handlers to handler list
        """
        # '.*$' will always match, so it will be last one
        last_one = None
        if self._handlers and self._handlers[-1][0] == r'.*$':
            last_one = self._handlers.pop()

        for route, handler in handlers:
            route = re.sub('{([-_a-zA-Z]+)}', '(?P<\g<1>>[^/?]+)', route)
            route += '$'
            compiled = re.compile(route)
            self._handlers.append((compiled, handler))

        if last_one:
            self._handlers.appned(last_one)


    def _find_handler(self, path):
        """Find the corresponding handler for the path
        if nothing mathed but having default handler, use default
        otherwise 404 Not Found
        """
        for route, handler_class in self._handlers:
            match = route.match(path)
            if match:
                return handler_class, match.groupdict()

        if self.settings.get('default_handler'):
            handler_class = self.settings['default_handler']
            return handler_class, {}

        # attenton !!!
        return ErrorHandler, None


    async def _parse_request(self, request_reader, response_writer):
        """parse data from StreamReader and build the request object
        """
        limit  = 2 ** 16
        req = Request()
        parser = HttpRequestParser(req)

        while True:
            data = await request_reader.read(limit)
            parser.feed_data(data)
            if req.finished or not data:
                break
            elif req.needs_wirte_continue:
                response_writer.write(b'HTTP/1.1 100 (Continue)\r\n\r\n')
                req.reset_state()

        req.method = parser.get_method().decode().upper()
        return req

    async def _route_request(self, handler_class, req, res):
        method = req.method
        if handler_class is None:
            raise HTTPError(404)

        handler = handler_class(self, req, res)
        await getattr(handler, method.lower())()

    async def _execute(self, request_reader, response_writer):
        res = Response()
        try:
            req = await self._parse_request(request_reader, response_writer)
            handler, args = self._find_handler(req.path)
            req.args = args

            try:
                await self._route_request(handler, req, res)
            except HTTPError as e:
                self.handle_error(res, e)

        except Exception as e:
            self.handle_error(res, e)

        self._write_response(res, response_writer)
        await response_writer.drain()
        response_writer.close()

    def handle_error(self, res, e):
        res.clear()
        if isinstance(e, HTTPError):
            res.status_codes = str(e.status_code)
            res.write(str(e))
        else:
            res.status_code = '500'
            res.write(res.status_code)
        # need logging
        traceback.print_exc()

    def _write_response(self, res, writer):
        writer.write(b'HTTP/1.1 %s\r\n' % (str(res.status_code).encode()))

        if 'Content-Length' not in res.headers:
            res.headers['Content-Length'] = str(sum(len(_) for _ in res._chunks))

        for key, value in res.headers.items():
            writer.write(key.encode() + b': ' + str(value).encode() + b'\r\n')

        for key, value in res.cookies.items():
            write_cookie(writer, key, value)

        writer.write(b'\r\n')

        for chunk in res._chunks:
            writer.write(chunk)
        writer.write_eof()

    def run(self, port=8080, host='127.0.0.1', debug=False):
        if debug:
            autoload()
        loop = asyncio.get_event_loop()
        print('Running on {}:{} (Press CTRL+C to quit)'.format(host, port))
        loop.create_task(asyncio.start_server(self._execute, host, port))
        loop.run_forever()
        loop.close()

