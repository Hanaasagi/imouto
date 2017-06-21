import re
import time
import asyncio
import traceback
import logging.config
from collections import Mapping, OrderedDict
from datetime import date as date_t, datetime, timedelta
from http.cookies import SimpleCookie
from imouto import Request, Response
from imouto.autoload import autoload
from imouto.log import access_log, app_log, DEFAULT_LOGGING
from imouto.util import hkey, hval, tob, touni, Singleton
from httptools import HttpRequestParser

# for type check
from typing import Tuple, List, Any

class HTTPError(Exception):
    """Exception represented HTTP Error
    """

    def __init__(self, status_code: int = 500, log_message: str = '',
                 *args) -> None:
        self.status_code = status_code
        self.log_message = log_message
        self.args = args
        if log_message and not args:
            self.log_message = log_message.replace('%', '%%')

    def __str__(self):
        if self.log_message:
            return "%s (%s)" % (message, self.log_message % self.args)
        return ''

def log(status_code: int, method: str, path: str, query_string: str) -> None:
    """logging the access message
    logging level depend http status code
    """
    if status_code >= 500:
        logger = access_log.error
    elif status_code >= 400:
        logger = access_log.warning
    else:
        logger = access_log.info

    if query_string:
        path = "%s?%s" % (path, query_string)
    logger('', extra={
        'status': status_code,
        'method': method,
        'path' :  path
    })


class RequestHandler:
    """Base class
    """

    def __init__(self, application, request: Request, response: Response,
                 **kwargs) -> None:
        """subclass should override initialize method rather than this
        """
        self.application = application
        self.request = request
        self.response = response
        self.initialize(**kwargs)

    def initialize(self, *args, **kwargs):
        """subclass initialization
        need to be overrided
        """
        pass

    async def prepare(self, *args, **kwargs):
        """invoked before get/post/.etc
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

    def write(self, chunk: str):
        """write data to the response buffer
        chunk may be other types for example None
        so call their `__str__` method to get string epresentation
        """
        self.response.write(chunk.__str__())

    def write_json(self, data: Any):
        """data will converted to json and write
        """
        # need enclosing try-except
        self.response.write_json(data)

    def redirect(self, url: str, permanent=False):
        """HTTP Redirect
        permanent determines 301 or 302
        """
        if permanent:
            self.response.status_code = 301
        else:
            self.response.status_code = 302
        self.response.headers['Location'] = url

    def get_query_argument(self, name: str, default: Any = None):
        """get parameter from query string
        """
        return self.request.query.get(name, default)

    def get_body_argument(self, name: str, default: Any = None):
        """get argument from request body
        """
        return self.request.form.get(name, default)

    @property
    def headers(self):
        return self.request.headers

    def get_header(self, name: str, default: Any = None):
        return self.headers.get(name, default)

    def set_header(self, name: str, value: str):
        self.response.headers[hkey(name)] = hval(value)

    @property
    def cookies(self):
        """request cookies
        """
        return self.request.cookies

    def get_cookie(self, name: str, default: Any = None):
        """get cookie from http request, can set default value
        """
        return self.cookies.get(name, default)

    def set_cookie(self, name: str, value: str, **options):
        """set cookie to http resposne
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
            raise ValueError('Cookie value to long.')

        self.response.cookies[name.strip()] = hval(value)

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
                value = time.strftime("%a, %d %b %Y %H:%M:%S GMT", value)
            self.response.cookies[name][key] = value

    def clear_cookie(self, key: str, **options):
        """make the cookie expired
        IE6, IE7, and IE8 does not support “max-age”, while (mostly)
        all browsers support expires
        """
        options['max_age'] = -1
        options['expires'] = 0
        self.set_cookie(key, '', **options)


class RedirectHandler(RequestHandler):
    """this handler do nothing, just redirect
    """

    def initialize(self, url: str, permanent=True):
        self._url = url
        self._permanent = permanent

    async def get(self):
        self.redirect(self._url, permanent=self._permanent)


# Maybe it make no sense
class ErrorHandler(RequestHandler):
    pass


class Application(metaclass=Singleton):
    """Application"""

    def __init__(self, handlers=None, **settings):
        self._handlers = OrderedDict()
        self.settings = settings

        if handlers:
            self.add_handlers(handlers)

        self.debug = settings.get('debug', False)
        self.default_handler = settings.get('default_handler', None)


    def add_handlers(self, handlers: List[Tuple[str, str]]):
        """Append handlers to handler list
        """
        # '.*$' will always match, so it will be last one
        last_one = None
        # if self._handlers and self._handlers[-1][0] == r'.*$':
        #     last_one = self._handlers.popitem()
        if self._handlers and r'.*$' in self._handlers.keys():
            last_one = self._handlers.pop(r'.*$')

        for route, handler in handlers:
            route = re.sub('{([-_a-zA-Z]+)}', '(?P<\g<1>>[^/?]+)', route)
            route += '$'
            compiled = re.compile(route)
            # self._handlers.append((compiled, handler))
            self._handlers[compiled] = handler

        if last_one:
            # self._handlers.appned(last_one)
            self._handlers[last_one[0]] = last_one[1]


    def _find_handler(self, path: str):
        """Find the corresponding handler for the path
        if nothing mathed but having default handler, use default
        otherwise 404 Not Found
        """
        for route, handler_class in self._handlers:
            match = route.match(path)
            if match:
                return handler_class, match.groupdict()

        return self.default_handler, {}


    async def _parse_request(self, request_reader: asyncio.StreamReader,
                             response_writer: asyncio.StreamWriter) -> Request:
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
            elif req.needs_write_continue:
                response_writer.write(b'HTTP/1.1 100 (Continue)\r\n\r\n')
                req.reset_state()

        req.method = touni(parser.get_method()).upper()
        return req

    async def _execute(self, handler_class: type,
                             req: Request, args):
        """"""
        res = Response()
        method = req.method
        if handler_class is None:
            raise HTTPError(404)

        if hasattr(handler_class, '_magic_route') and handler_class._magic_route:
            await getattr(handler_class, method.lower())(req, res, **args)
        else:
            handler = handler_class(self, req, res)
            await getattr(handler, method.lower())(**args)
        return res

    async def __call__(self, request_reader: asyncio.StreamReader,
                       response_writer: asyncio.StreamWriter):
        try:
            req = await self._parse_request(request_reader, response_writer)
            handler_class, args = self._find_handler(req.path)
            try:
                res = await self._execute(handler_class, req, args)
            except HTTPError as e:
                res = self._handle_error(e)
        except Exception as e:
            res = self._handle_error(e)

        # output the access log)
        log(status_code=res.status_code, method=req.method,
            path=req.path, query_string=req.query_string)
        self._write_response(res, response_writer)
        await response_writer.drain()
        response_writer.close()

    def _handle_error(self, e: Exception):
        res = Response()
        # clear the response body when there is an exception
        res.clear()
        if isinstance(e, HTTPError):
            res.status_code = e.status_code
            res.write(str(e))
        else:
            res.status_code = 500
            # only debug mode should show traceback
            if self.debug:
                res.write('\n' + traceback.format_exc())
        return res

    def _write_response(self, res, writer: asyncio.StreamWriter):
        """get chunk from Response object and build http resposne"""
        writer.write(res.output())
        writer.write_eof()

    def convert(self):
        """convert self._handlers to list"""
        # I use orderdict to for magicroute but iter a orderdict is too slow
        # so convert it to list before app run
        if isinstance(self._handlers, OrderedDict):
            self._handlers = list(self._handlers.items())


    def run(self, *, host: str = '127.0.0.1', port: int = 8080,
            loop_policy: asyncio.AbstractEventLoopPolicy = None,
            log_config: dict = DEFAULT_LOGGING):
        self.convert()
        """run"""
        if self.debug:
            autoload()
        logging.config.dictConfig(log_config)
        if loop_policy:
            # For example `uvloop` can improve performance significantly
            # import uvloop
            # asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            asyncio.set_event_loop_policy(loop_policy)

        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        app_log.info('Running on %s:%s %s(Press CTRL+C to quit)'
                     % ( host, port, '[debug mode]' if self.debug else ''))
        # mypy doesn't know self mean, use self.__call__ explicitly
        coro = asyncio.start_server(self.__call__, host, port, loop=loop)
        server = loop.run_until_complete(coro)
        # loop.create_task(asyncio.start_server(self.__call__, host, port))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

