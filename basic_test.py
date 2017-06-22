import asyncio
from imouto.web import Application, RequestHandler
from imouto.magicroute import GET, POST

class MainHandler(RequestHandler):

    async def get(self, name):
        await asyncio.sleep(0.1)
        # cookie test
        self.write(self.get_cookie('test', 'test'))
        self.set_cookie('name', 'imouto')
        self.write('Hello, %s' % name)

class ArgumentHandler(RequestHandler):

    async def get(self):
        # query string test
        self.write('query ' + (self.get_query_argument('neko') or 'None'))

    async def post(self):
        # body test
        self.write('form ' + (self.get_body_argument('neko') or 'None'))

class HeaderTestHandler(RequestHandler):

    async def get(self):
        # header test
        self.write('your Accept-Encoding is {}\n'.format(
        self.headers['Accept-Encoding']))
        self.set_header('access-token', '123456')

class RHandler(RequestHandler):

    async def get(self):
        self.redirect('/妹')

class JsonHandler(RequestHandler):

    async def get(self):
        try:
            self.write_json(dict(a=1,b=2))
        except Exception as e:
            print(e)

class BugHandler(RequestHandler):

    async def get(self):
        raise Exception('I hate bugs...')

class HelloHandler(RequestHandler):

    async def get(self):
        self.write('Hello World')

app = Application([
    (r'/', HelloHandler),
    (r'/(\d+)', MainHandler),
    (r'/redirect/', RHandler),
    (r'/bugs/', BugHandler),
    (r'/argument/', ArgumentHandler),
    (r'/header', HeaderTestHandler),
    (r'/api/', JsonHandler)], debug=True)

async def magic_get(request, resposne):
    resposne.write("it's magic route")

async def magic_post(request, response):
    response.write('wow')

GET / '/magic/' > magic_get
POST / '/magic/' > magic_post

app.run()
