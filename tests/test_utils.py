# flake8: noqa

import pytest
from imouto.utils import *


def test_url_encode():
    data_encoded= url_encode('www.google.com.hk/#safe=strict&q=python3 url escape')
    assert data_encoded == 'www.google.com.hk%2F%23safe%3Dstrict%26q%3Dpython3+url+escape'

    data_encoded = url_encode('www.google.com.hk/#safe=strict&q=python3 url escape', plus=False)
    assert data_encoded == 'www.google.com.hk/%23safe%3Dstrict%26q%3Dpython3%20url%20escape'


def test_re_unescape():
    assert '\\d+' == re_unescape(r'\\d+')

    with pytest.raises(ValueError):
        re_unescape(r'\d')

def test_trim_keys():
    assert trim_keys({' name': 'value'}) == {'name': 'value'}


def test_tob():
    assert tob(u'妹') == b'\xe5\xa6\xb9'
    assert tob(None) == b''


def test_touni():
    assert touni(b'\xe5\xa6\xb9') == u'妹'
    assert touni(None) == ''


def test_hkey():
    assert hkey('content_type') == 'Content-Type'
    with pytest.raises(ValueError):
        hkey('content_type\n')


def test_hval():
    assert hval('text/plain') == 'text/plain'
    with pytest.raises(ValueError):
        hval('text/plain\n')


def test_singleton():

    class A(metaclass=Singleton):
        pass

    a1 = A()
    a2 = A()
    assert a1 is a2

    class B(metaclass=Singleton):
        pass

    b = B()
    assert b is not a1
