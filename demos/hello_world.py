from imouto.web import RequestHandler, Application


class HelloWorldHandler(RequestHandler):

    def initialize(self):
        self.hoge = "Hello World "

    async def get(self, name):
        self.write(self.hoge + name)

app = Application([(r'/(\w+)', HelloWorldHandler)], debug=True)
app.run()

