# imōto(妹)
[![Build Status](https://travis-ci.org/Hanaasagi/imouto.svg?branch=master)](https://travis-ci.org/Hanaasagi/imouto)
![Completion](https://img.shields.io/badge/completion-30%25-39C5BB.svg)
![Python Version](https://img.shields.io/badge/Python-v3.5-orange.svg)
[![License](https://img.shields.io/badge/license-BSD3-blue.svg)](https://github.com/Hanaasagi/imouto/blob/master/LICENSE)
![Platform](https://img.shields.io/badge/platform-Linux-BE84B8.svg)
![release](https://img.shields.io/badge/release-dev-EA0032.svg)  

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

### Features

#### 1) magic route

```Python
GET / '/' > hello   # it will match '/' call `hello`
POST / '/mahou' > shoujo  # it will match '/mahou' and call `shoujo` 
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


### Benchmark

```
➜  ~ wrk -t2 -c600 -d30s http://127.0.0.1:8080
Running 30s test @ http://127.0.0.1:8080
  2 threads and 600 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   262.48ms   64.72ms   1.82s    95.75%
    Req/Sec   703.67    264.06     1.66k    68.96%
  42054 requests in 30.03s, 3.53MB read
  Socket errors: connect 0, read 41976, write 0, timeout 37
Requests/sec:   1400.23
Transfer/sec:    120.33KB
```

### License

This software is free to use under the BSD license. See the [LICENSE file](https://github.com/Hanaasagi/imouto/blob/master/LICENSE) for license text and copyright information.
