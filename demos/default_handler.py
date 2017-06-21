from imouto.web import RequestHandler, Application


class DefaultHandler(RequestHandler):

    async def get(self):
        self.write("it's default handler")


app = Application(deubg=True, default_handler=DefaultHandler)
app.run()
