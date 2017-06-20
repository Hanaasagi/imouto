import time
import hmac
import base64
import hashlib
from imouto.util import tob, touni


def create_secure_value(name, value, *, secret):
    """create secure value
    will be following format
    b'base64 value|timestamp|signature'
    """
    timestamp = tob(str(int(time.time())))
    value = base64.b64encode(tob(value))
    signature = _generate_signature(secret, name, value, timestamp)
    return  b"|".join((value, timestamp, signature))


def _generate_signature(secret, *parts):
    """generate signature using sha1
    """
    hash_ = hmac.new(tob(secret), digestmod=hashlib.sha1)
    for part in parts:
        hash_.update(tob(part))
    result = tob(hash_.hexdigest())
    return result


def verify_secure_value(name, value, *, secret):
    """verify the signature
    if correct return the value after base64 decode
    else return None
    """
    parts = tob(value).split(b"|")
    if len(parts) != 3:
        return None

    signature = _generate_signature(secret, name, parts[0], parts[1])
    # print(signature, parts[2])
    if not hmac.compare_digest(parts[2], signature):
        return None
    else:
        return touni(base64.b64decode(parts[0]))


if __name__ == '__main__':
    # fake `time.time`
    time.time = lambda: 1497854241.6677122
    value = create_secure_value('test', '23333', secret='root')
    assert value == b'MjMzMzM=|1497854241|d1bc51b38323add85ae80a9f130d3b5440026cca'
    assert verify_secure_value('test', value, secret='root') == '23333'
