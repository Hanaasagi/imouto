# imōto(妹)
Asynchronous Web API Framework based on `asyncio`  
*It only work on the version aboved 3.5*

### Introduction

![](https://github.com/Hanaasagi/imouto/blob/master/.resources/logo.png)

I think it should like this:

```Python
import asyncio
from imouto.web import Application
from imouto.web import RequestHandler


class MainHandler(RequestHandler):

    async def get(self):
        await asyncio.sleep(0.1)
        self.response.write('俺は妹が大好きだ')


app = Application()
app.add_route('/', MainHandler)
app.run(debug=True)
```


### Documentation

...

### TODO

- [ ] basic functions
- [ ] support GraphQL
- [ ] unittest
- [ ] documentation


### License

This software is free to use under the BSD license. See the [LICENSE file](https://github.com/Hanaasagi/imouto/blob/master/LICENSE) for license text and copyright information.
