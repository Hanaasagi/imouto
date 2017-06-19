from imouto.web import RequestHandler, Application


class HeaderDemo(RequestHandler):

    async def get(self):
        # header test
        self.write('your Accept-Encoding is {}\n'.format(
            self.headers['Accept-Encoding']))
        self.set_header('access-token', '123456')

app = Application([(r'/', HeaderDemo)])
app.run()
