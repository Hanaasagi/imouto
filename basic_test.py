import asyncio
from imouto.web import Application, RequestHandler

class MainHandler(RequestHandler):

    async def get(self, name):
        await asyncio.sleep(0.1)
        print('after 0.1 sec')
        # header test
        self.write('your Accept-Encoding is {}\n'.format(
            self.headers['Accept-Encoding']))
        self.set_header('access-token', '123456')
        # cookie test
        self.write(self.get_cookie('test', 'test'))
        self.set_cookie('name', 'imouto')
        self.write('Hello, %s' % name)

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

app = Application([
    (r'/{name}', MainHandler),
    (r'/', RHandler),
    (r'/bugs/', BugHandler),
    (r'/api/', JsonHandler)], debug=True)
app.run()
