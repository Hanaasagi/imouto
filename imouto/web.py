class RequestHandler:

    def __init__(self, application, request, response, **kwargs):
        self.application = application
        self.request = request
        self.response = response
        self.initialize(**kwargs)

    def initialize(self):
        pass

    async def prepare(self):
        pass

    async def head(self, *args, **kwargs):
        raise HTTPError(405)

    async def get(self, *args, **kwargs):
        raise HTTPError(405)

    async def post(self, *args, **kwargs):
        raise HTTPError(405)

    async def delete(self, *args, **kwargs):
        raise HTTPError(405)

    async def patch(self, *args, **kwargs):
        raise HTTPError(405)

    async def put(self, *args, **kwargs):
        raise HTTPError(405)

    async def options(self, *args, **kwargs):
        raise HTTPError(405)


