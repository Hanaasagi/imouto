from imouto.web import RequestHandler, Application


class CookieDemo(RequestHandler):

    async def get(self):
        self.write('your cookie ' + self.get_cookie('cookie_name', 'unknown'))
        self.set_cookie('cookie_name', 'imouto')


app = Application([(r'/', CookieDemo)])
app.run()
