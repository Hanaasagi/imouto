import asyncio
from aiohttp import ClientSession
from time import time

url = 'http://127.0.0.1:8080/hello'

async def hello():
    async with ClientSession() as session:
        print('getting')
        start = time()
        async with session.get(url) as response:
            response = await response.read()
            dur = time() - start
            print('read response, took %.5f' % dur)



loop = asyncio.get_event_loop()

tasks = []
for i in range(100):
    task = asyncio.ensure_future(hello())
    tasks.append(task)
loop.run_until_complete(asyncio.wait(tasks))
