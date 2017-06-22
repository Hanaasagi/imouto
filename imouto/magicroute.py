from imouto.web import Application
from imouto.route import URLSpec


class MagicRoute:
    __slots__ = ['_magic_route', 'get', 'post', 'head', 'put',
                 'patch', 'trace', 'options', 'connect', 'delete']


class Route:

    def __init__(self, method, path):
        self.method = method
        self.path = path

    def __gt__(self, handler):
        # TODO refactoring the ugly code, try to replace the Slot
        app = Application()
        if self.path in app._handlers:
            setattr(app._handlers[self.path].handler_class,
                    self.method.lower(), handler)
        else:
            obj = MagicRoute()
            setattr(obj, '_magic_route', True)
            setattr(obj, self.method.lower(), handler)
            # Application is singleton
            app._handlers[self.path] = URLSpec(self.path, obj)


class HTTPMethod(type):

    def __truediv__(self, path):
        return Route(self.__name__, path)


class GET(metaclass=HTTPMethod):
    pass


class POST(metaclass=HTTPMethod):
    pass


class HEAD(metaclass=HTTPMethod):
    pass


class OPTIONS(metaclass=HTTPMethod):
    pass


class DELETE(metaclass=HTTPMethod):
    pass


class PUT(metaclass=HTTPMethod):
    pass
