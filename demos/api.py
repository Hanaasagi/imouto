from collections import namedtuple
from imouto.web import RequestHandler, Application


class JsonDemo(RequestHandler):

    async def get(self):
        T = namedtuple('T', ['neko'])
        self.write_json(
            T(self.get_query_argument('neko', 'unknown'))
        )

    async def post(self):
        self.write_json({
            'neko': self.get_body_argument('neko')
        })


app = Application([(r'/', JsonDemo)])
app.run()
