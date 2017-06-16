import asyncio
from imouto.web import Application, RequestHandler

class MainHandler(RequestHandler):

    async def get(self, name):
        await asyncio.sleep(0.1)
        self.write('Hello, %s' % name)

class RHandler(RequestHandler):

    async def get(self):
        self.redirect('/妹')

class JsonHandler(RequestHandler):

    async def get(self):
        self.write_json(dict(a=1,b=2))

app = Application([
    (r'/{name}', MainHandler),
    (r'/', RHandler),
    (r'/api/', JsonHandler)])
app.run(debug=True)
