import asyncio
import traceback
import logging.config
from collections import OrderedDict
from imouto import Request, Response
from imouto.autoload import autoload
from imouto.route import URLSpec
from imouto.log import access_log, app_log, DEFAULT_LOGGING
from imouto.utils import hkey, hval, touni, Singleton
from imouto.errors import HTTPError, MethodNotAllowed  # type: ignore
from httptools import HttpRequestParser

# for type check
from typing import Tuple, List, Mapping, Any


def log(status_code: int, method: str, path: str, query_string: str) -> None:
    """ logging the access message
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
        'path': path
    })


class RequestHandler:
    """ Base class """

    def __init__(self, app, request: Request, response: Response,
                 **kwargs) -> None:
        """subclass should override initialize method rather than this
        """
        self.app = app
        self.request = request
        self.response = response
        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        """ subclass initialization need to be overrided """

    async def prepare(self, *args, **kwargs):
        """ invoked before get/post/.etc """

    async def head(self, *args, **kwargs):
        raise MethodNotAllowed  # pragma: no cover

    async def get(self, *args, **kwargs):  # pragma: no cover
        raise MethodNotAllowed

    async def post(self, *args, **kwargs):
        raise MethodNotAllowed  # pragma: no cover

    async def delete(self, *args, **kwargs):
        raise MethodNotAllowed  # pragma: no cover

    async def patch(self, *args, **kwargs):
        raise MethodNotAllowed  # pragma: no cover

    async def put(self, *args, **kwargs):
        raise MethodNotAllowed  # pragma: no cover

    async def options(self, *args, **kwargs):
        raise MethodNotAllowed  # pragma: no cover

    def write(self, chunk: str):
        """ write data to the response buffer
        chunk may be other types for example None
        so call their `__str__` method to get string epresentation
        """
        self.response.write(chunk.__str__())

    def write_json(self, data: Any):
        """ data will converted to json and write """
        # need enclosing try-except
        self.response.write_json(data)

    def redirect(self, url: str, permanent: bool = False):
        """ HTTP Redirect permanent determines 301 or 302 """
        if permanent:
            self.response.status_code = 301
        else:
            self.response.status_code = 302
        self.response.headers['Location'] = url

    def get_query_argument(self, name: str, default: Any = None):
        """ get parameter from query string """
        return self.request.query.get(name, default)

    def get_body_argument(self, name: str, default: Any = None):
        """ get argument from request body """
        return self.request.form.get(name, default)

    @property
    def headers(self):
        """ return all headers """
        return self.request.headers

    def get_header(self, name: str, default: Any = None):
        """ get specified header from request header """
        return self.headers.get(name, default)

    def set_header(self, name: str, value: str):
        """ set response header """
        self.response.headers[hkey(name)] = hval(value)

    @property
    def cookies(self):
        """ return all request cookies """
        return self.request.cookies

    def get_cookie(self, name: str, default: Any = None):
        """ get cookie from http request """
        return self.cookies.get(name, default)

    def set_cookie(self, name: str, value: str, **options):
        return self.response.set_cookie(name, value, **options)

    def clear_cookie(self, key: str, **options):
        return self.response.clear_cookie(key, **options)


class RedirectHandler(RequestHandler):
    """this handler do nothing, just redirect
    """

    def initialize(self, **kwargs):
        self._url: str = kwargs.get('url', '/')
        self._permanent: bool = kwargs.get('permanent', True)

    async def get(self):
        self.redirect(self._url, permanent=self._permanent)


class Application(metaclass=Singleton):
    """ Base Application implemention"""

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
        for route, handler in handlers:
            self._handlers[route] = URLSpec(route, handler)

    def _find_handler(self, path: str):
        """Find the corresponding handler for the path
        if nothing mathed but having default handler, use default
        otherwise 404 Not Found
        """

        path_args: List[str] = []
        path_kwargs: Mapping[str, str] = {}
        for spec in self._handlers:
            match = spec.regex.match(path)
            if match:
                handler_class = spec.handler_class
                # TODO
                # handler_kwargs = spec.kwargs
                if spec.regex.groups:
                    if spec.regex.groupindex:
                        path_kwargs = match.groupdict()
                    else:
                        path_args = match.groups()
                return handler_class, path_args, path_kwargs
        return self.default_handler, path_args, path_kwargs

    async def _parse_request(self, request_reader: asyncio.StreamReader,
                             response_writer: asyncio.StreamWriter) -> Request:
        """parse data from StreamReader and build the request object
        """
        limit = 2 ** 16
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
                       req: Request, args, kwargs):
        """"""
        method = req.method
        if handler_class is None:
            raise HTTPError(404)

        res = Response()
        is_magic_route = getattr(handler_class, '_magic_route', False)
        if is_magic_route:
            await getattr(handler_class, method.lower())(
                req, res, *args, **kwargs)
        else:
            handler = handler_class(self, req, res)
            await getattr(handler, method.lower())(*args, **kwargs)
        return res

    async def __call__(self, request_reader: asyncio.StreamReader,
                       response_writer: asyncio.StreamWriter):
        try:
            req = await self._parse_request(request_reader, response_writer)
            handler_class, args, kwargs = self._find_handler(req.path)
            try:
                res = await self._execute(handler_class, req, args, kwargs)
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

    def _prepare(self):
        """convert self._handlers to list"""
        # I use orderdict to for magicroute but iter a orderdict is too slow
        # so convert it to list before app run
        if isinstance(self._handlers, OrderedDict):
            self._handlers = list(self._handlers.values())

    def test_server(self, loop: asyncio.AbstractEventLoop):
        """only for unittest"""
        # only here use this module
        import socket
        sock = socket.socket()
        sock.bind(('127.0.0.1', 0))
        self._prepare()
        coro = asyncio.start_server(self.__call__, sock=sock, loop=loop)
        server = loop.run_until_complete(coro)
        return server, sock.getsockname()

    def run(self, *, host: str = '127.0.0.1', port: int = 8080,
            loop_policy: asyncio.AbstractEventLoopPolicy = None,
            log_config: dict = DEFAULT_LOGGING):
        self._prepare()
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
                     % (host, port, '[debug mode]' if self.debug else ''))
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
