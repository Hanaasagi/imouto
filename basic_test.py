import unittest
from imouto.web import Application
from imouto.web import RequestHandler
import asyncio


class Handler(RequestHandler):

    async def get(self):
        await asyncio.sleep(0.1)
        self.response.write('Hello, %s' % self.request.args['name'])

class BasicTest(unittest.TestCase):
    pass


app = Application([
    (r'/{name}', Handler)])
app.run(debug=True)
