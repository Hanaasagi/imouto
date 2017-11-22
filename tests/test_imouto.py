from imouto.web import RequestHandler, Application
from imouto.magicroute import GET


def test_basic(client):
    class HelloWorldHandler(RequestHandler):

        async def get(self):
            self.write("Hello World")

    app = Application([
        (r'/', HelloWorldHandler),
    ])
    client.feed(app)
    response = client.get('/')
    response_correct = [
        b'HTTP/1.1 200 OK',
        b'Content-Type: text/html',
        b'Content-Length: 11',
        b'',
        b'Hello World'
    ]
    assert sorted(response.split(b'\r\n')) == \
        sorted(response_correct)


def test_redirect(client):
    class RedirectHandler(RequestHandler):

        async def get(self):
            self.redirect('/')

    app = Application([
        (r'/redirect/', RedirectHandler),
    ])
    client.feed(app)
    response = client.get('/redirect/')
    assert b'302 Found' in response
    assert b'Location: /' in response


def test_magic_route(client):
    async def Ahandler(res, req):
        req.write('It is magic route')
    GET / '/magic/' > Ahandler

    client.feed(Application())
    response = client.get('/magic/')
    assert b'It is magic route' in response


def test_http_method(client):
    class MethodHandler(RequestHandler):

        async def get(self):
            self.write('GET')

        async def post(self):
            self.write('POST')
    app = Application([
        (r'/method/', MethodHandler),
    ])
    client.feed(app)
    response = client.get('/method/')
    assert b'GET' in response
    response = client.post('/method/')
    assert b'POST' in response


def test_dynamic_route(client):
    class DynamicHandler(RequestHandler):

        async def get(self, id_):
            self.write('id: ' + id_)

    app = Application([
        (r'/(\d+)/', DynamicHandler),
    ])
    client.feed(app)
    response = client.get('/2333/')
    assert b'id: 2333', response


def test_get_query_string(client):
    class QueryHandler(RequestHandler):

        async def get(self):
            a = self.get_query_argument('a')
            b = self.get_query_argument('b')
            sum_ = int(a) + int(b)
            self.write('sum: {}'.format(sum_))

    app = Application([
        (r'/query/', QueryHandler),
    ])
    client.feed(app)
    response = client.get('/query/?a=22&b=33')
    assert b'sum: 55', response


def test_post_data(client):
    class PostHandler(RequestHandler):
        async def post(self):
            a = self.get_body_argument('a')
            b = self.get_body_argument('b')
            product = int(a) * int(b)
            self.write('product: {}'.format(product))

    app = Application([
        (r'/post/', PostHandler),
    ])
    client.feed(app)
    content_type = b'application/x-www-form-urlencoded; charset=utf-8'
    content_length = b'9'
    response = client.post('/post/', data=b'a=33&b=22',
                           content_type=content_type,
                           content_length=content_length)
    assert b'product: 726', response
