import asyncio
from imouto.web import Application, RequestHandler

class MainHandler(RequestHandler):

    async def get(self):
        await asyncio.sleep(0.1)
        self.write('Hello, %s' % self.request.args['name'])

class RHandler(RequestHandler):

    async def get(self):
        self.redirect('/妹')


app = Application([
    (r'/{name}', MainHandler),
    (r'/', RHandler)])
app.run(debug=True)
