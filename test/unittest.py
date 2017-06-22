import unittest
import asyncio
import gc
from asyncio import test_utils
from imouto.web import RequestHandler, Application
from imouto.magicroute import GET
from imouto.util import tob, hkey


async def client(addr, loop, request_data):
    reader, writer = await asyncio.open_connection(*addr, loop=loop)
    # send a line
    writer.write(request_data)
    # read it back
    response_data = await reader.read()
    writer.close()
    return response_data


class ImoutoTests(test_utils.TestCase):

    def setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    def tearDown(self):
        # just in case if we have transport close callbacks
        test_utils.run_briefly(self.loop)

        self.loop.close()
        gc.collect()
        super().tearDown()

    def get_response(self, request_data):
        server, addr = app.test_server(self.loop)
        response_data = self.loop.run_until_complete(
            asyncio.Task(client(addr, self.loop, request_data),
                         loop=self.loop))
        server.close()
        self.loop.run_until_complete(server.wait_closed())
        return response_data

    def generate_request(self, method=b'GET', path=b'/', version=b'1.1',
                         accept=b'*/*', accept_encoding=b'gzip, deflate',
                         connection=b'Keep-alive', body=b'', **options):
        headers = [b'%b: %b\r\n' % (tob(hkey(key)), tob(value))
                   for key, value in options.items()]
        return (b'%b %b HTTP/%b\r\n'
                b'Accept: %b\r\n'
                b'Accept-Encoding: %b\r\n'
                b'Connection: %b\r\n'
                b'%b'
                b'\r\n'
                b'%b' % (
                    method, path, version,
                    accept,
                    accept_encoding,
                    connection,
                    b''.join(headers),
                    body))

    def test_basic(self):
        request_data = self.generate_request()
        response_data = self.get_response(request_data)
        response_data_correct = [b'HTTP/1.1 200 OK',
                                 b'Content-Type: text/html',
                                 b'Content-Length: 11',
                                 b'',
                                 b'Hello World']
        self.assertEqual(sorted(response_data.split(b'\r\n')),
                         sorted(response_data_correct))

    def test_redirect(self):
        request_data = self.generate_request(path=b'/redirect/')
        response_data = self.get_response(request_data)
        self.assertIn(b'302 Found', response_data)
        self.assertIn(b'Location: /', response_data)

    def test_magic_route(self):
        request_data = self.generate_request(path=b'/magic/')
        response_data = self.get_response(request_data)
        self.assertIn(b'It is magic route', response_data)

    def test_http_method(self):
        for m in (b'GET', b'POST'):
            request_data = self.generate_request(path=b'/method/', method=m)
            response_data = self.get_response(request_data)
            self.assertIn(m, response_data)

    def test_dynamic_route(self):
        request_data = self.generate_request(path=b'/2333/')
        response_data = self.get_response(request_data)
        self.assertIn(b'id: 2333', response_data)

    def test_get_query_string(self):
        request_data = self.generate_request(path=b'/query/?a=22&b=33')
        response_data = self.get_response(request_data)
        self.assertIn(b'sum: 55', response_data)

    def test_post_data(self):
        content_type = b'application/x-www-form-urlencoded; charset=utf-8'
        request_data = self.generate_request(method=b'POST', path=b'/post/',
                                             content_type=content_type,
                                             content_length=b'9',
                                             body=b'a=33&b=22')
        response_data = self.get_response(request_data)
        self.assertIn(b'product: 726', response_data)


class HelloWorldHandler(RequestHandler):

    async def get(self):
        self.write("Hello World")


class RedirectHandler(RequestHandler):

    async def get(self):
        self.redirect('/')


class MethodHandler(RequestHandler):

    async def get(self):
        self.write('GET')

    async def post(self):
        self.write('POST')


class DynamicHandler(RequestHandler):

    async def get(self, id_):
        self.write('id: ' + id_)


class QueryHandler(RequestHandler):

    async def get(self):
        a = self.get_query_argument('a')
        b = self.get_query_argument('b')
        sum_ = int(a) + int(b)
        self.write('sum: {}'.format(sum_))


class PostHandler(RequestHandler):

    async def post(self):
        a = self.get_body_argument('a')
        b = self.get_body_argument('b')
        product = int(a) * int(b)
        self.write('product: {}'.format(product))


app = Application([
    (r'/', HelloWorldHandler),
    (r'/redirect/', RedirectHandler),
    (r'/method/', MethodHandler),
    (r'/(\d+)/', DynamicHandler),
    (r'/query/', QueryHandler),
    (r'/post/', PostHandler),
])


async def Ahandler(res, req):
    req.write('It is magic route')
GET / '/magic/' > Ahandler


if __name__ == '__main__':
    unittest.main()
