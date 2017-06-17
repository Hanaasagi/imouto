# imōto(妹)
[![Build Status](https://travis-ci.org/Hanaasagi/imouto.svg?branch=master)](https://travis-ci.org/Hanaasagi/imouto)

Asynchronous Web API Framework based on `asyncio`  
*It only work on the version aboved 3.5*

### Introduction
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

- [x] basic functions
- [x] debug mode
- [ ] support GraphQL
- [ ] unittest
- [ ] add CI
- [ ] documentation


### License

This software is free to use under the BSD license. See the [LICENSE file](https://github.com/Hanaasagi/imouto/blob/master/LICENSE) for license text and copyright information.
