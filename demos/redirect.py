from imouto.web import RequestHandler, Application, RedirectHandler


class Redirect_1(RequestHandler):

    async def get(self):
        self.redirect('/2')


class Redirect_2(RequestHandler):

    async def get(self):
        self.write('redirect successful')


app = Application([
    (r'/1', Redirect_1),
    (r'/2', Redirect_2)
])
app.run()

