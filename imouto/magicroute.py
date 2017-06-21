import re
from imouto.web import Application


class MagicRoute:
    pass


class Route:

    def __init__(self, method, path):
        self.method = method
        self.path = path

    def __gt__(self, handler):
        # TODO refactoring the ugly code, try to replace the Slot
        app = Application()
        route = re.sub('{([-_a-zA-Z]+)}', '(?P<\g<1>>[^/?]+)', self.path)
        route += '$'
        compiled = re.compile(route)
        o = app._handlers.get(compiled, MagicRoute())
        setattr(o, '_magic_route', True)
        setattr(o, self.method.lower(), handler)
        # Application is singleton
        app._handlers[compiled] = o


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
