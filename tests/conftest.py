import gc
import asyncio
import pytest
from asyncio import test_utils
from imouto.utils import tob, hkey


class Client(test_utils.TestCase):

    def setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    def tearDown(self):
        # just in case if we have transport close callbacks
        test_utils.run_briefly(self.loop)

        self.loop.close()
        # clear
        type(self.app)._instances = {}
        gc.collect()
        super().tearDown()

    def _generate_request(self, method=b'GET', path=b'/', version=b'1.1',
                          accept=b'*/*', accept_encoding=b'gzip, deflate',
                          connection=b'Keep-alive', data=b'', **options):
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
                    data))

    def feed(self, app):
        self.app = app

    def _get_response(self, request_data):

        async def client(addr, loop, request_data):
            reader, writer = await asyncio.open_connection(*addr, loop=loop)
            # send a line
            writer.write(request_data)
            # read it back
            response_data = await reader.read()
            writer.close()
            return response_data

        server, addr = self.app.test_server(self.loop)
        response_data = self.loop.run_until_complete(
            asyncio.Task(client(addr, self.loop, request_data),
                         loop=self.loop))
        server.close()
        self.loop.run_until_complete(server.wait_closed())
        return response_data

    def get(self, path, **headers):
        request = self._generate_request(path=tob(path),
                                         method=b'GET', **headers)
        response = self._get_response(request)
        return response

    def post(self, path, **headers):
        request = self._generate_request(path=tob(path),
                                         method=b'POST', **headers)
        response = self._get_response(request)
        return response


@pytest.fixture
def client():
    client = Client()
    client.setUp()
    yield client
    client.tearDown()
