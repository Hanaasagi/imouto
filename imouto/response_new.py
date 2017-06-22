from imouto.util import tob, touni


class BaseHTTPResponse:

    def _encode_body(self, data):
        return tob(data)

    def _parse_headers(self):
        headers = []
        for name, value in self.headers.items():
            headers.append(b"%b: %b\r\n" % (tob(name), touni(value)))
        return b"".join(headers)

    @property
    def cookies(self):
        pass
