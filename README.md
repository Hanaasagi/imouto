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
GET / '' > hello   # it will match '/' call `hello`
POST / 'mahou' > shoujo  # it will match '/mahou' and call `shoujo` 
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


### Performance

```
tornado_test        imouto_test         imouto_with_uvloop
0.8195919742584229  0.6870878856182099  0.592484435081482
0.8447552053928375  0.6916719167232513  0.6349048058986664
0.8576259860992431  0.7158290717601776  0.6944666051864624
0.8763608188629151  0.7358270277976989  0.8766378736495972
0.909332069158554   0.7691210973262786  0.9184057350158692
0.9210720345973968  0.7733446607589721  0.930897155046463
0.9559958589076996  0.8765601601600647  0.9368923835754395
0.9733685319423675  0.8806607291698456  0.9659890236854554
0.9867800929546356  0.9735530288219452  1.0098846964836121
1.0865532035579184  1.60449635720253    1.1345730767250062
```

### License

This software is free to use under the BSD license. See the [LICENSE file](https://github.com/Hanaasagi/imouto/blob/master/LICENSE) for license text and copyright information.
