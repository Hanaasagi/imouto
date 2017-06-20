from imouto.web import Application
from imouto.magicroute import GET, POST


async def hello_world_get(request, response):
    response.write("Hello World, it'is get")


async def hello_world_post(request, resposne):
    resposne.write("Hello World, it'is post")


GET  / '/' > hello_world_get
POST / '/' > hello_world_post

app = Application()
app.run()
