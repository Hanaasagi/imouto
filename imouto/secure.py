import time
import hmac
import base64
import hashlib
from imouto.httputils import tob, touni


def create_signature(name, value, *, secret):
    """generate signature
    """
    timestamp = tob(str(int(time.time())))
    value = base64.b64encode(tob(value))
    signature = _generate_signature(secret, name, value, timestamp)
    return  b"|".join((value, timestamp, signature))


def _generate_signature(secret, *parts):
    hash_ = hmac.new(tob(secret), digestmod=hashlib.sha1)
    for part in parts:
        hash_.update(tob(part))
    return tob(hash_.hexdigest())


def check_signature(name, value, *, secret):
    parts = tob(value).split(b"|")
    if len(parts) != 3:
        return None

    signature = _generate_signature(secret, name, parts[0], parts[1])
    if not hmac.compare_digest(parts[2], signature):
        return None
    else:
        return touni(base64.b64decode(parts[0]))


if __name__ == '__main__':
    # fake
    time.time = lambda: 1497854241.6677122
    value = create_signature('test', '23333', secret='root')
    assert value == b'MjMzMzM=|1497854241|d1bc51b38323add85ae80a9f130d3b5440026cca'
    assert check_signature('test', value, secret='root') == '23333'
