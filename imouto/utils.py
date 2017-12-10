import re
import urllib.parse
from string import ascii_letters, digits
from collections import UserDict, Iterable

from typing import Mapping

"""Some utility functions and classes"""


def url_encode(value, plus=True):
    """urlencode
    if plus is True ' ' will convert to '+'
    otherwise ' ' will convert to '%20'
    >>> url_encode('www.google.com.hk/#safe=strict&q=python3 url escape')
    'www.google.com.hk%2F%23safe%3Dstrict%26q%3Dpython3+url+escape'
    >>> url_encode('www.google.com.hk/#safe=strict&q=python3 url escape',False)
    'www.google.com.hk/%23safe%3Dstrict%26q%3Dpython3%20url%20escape'
    """
    quote = urllib.parse.quote_plus if plus else urllib.parse.quote
    return quote(tob(value))


def re_unescape(s):
    _re_unescape_pattern = re.compile(r'\\(.)', re.DOTALL)
    _alphanum = list(ascii_letters + digits)

    def _re_unescape_replacement(match):
        group = match.group(1)
        if group[0] in _alphanum:
            raise ValueError(r"cannot unescape '\\%s'" % group[0])
        return group

    return _re_unescape_pattern.sub(_re_unescape_replacement, s)


def trim_keys(dict_):
    """remove dict keys with leading and trailing whitespace
    >>> trim_keys({' name': 'value'}) == {'name': 'value'}
    True
    """
    return {k.strip(): v for k, v in dict_.items()}


# Some helpers for string/byte handling
def tob(s, enc='utf8'):
    if isinstance(s, str):
        return s.encode(enc)
    return b'' if s is None else bytes(s)


def touni(s, enc='utf8', err='strict'):
    if isinstance(s, bytes):
        return s.decode(enc, err)
    return '' if s is None else str(s)


def hkey(key):
    """
    >>> hkey('content_type')
    'Content-Type'
    """
    if '\n' in key or '\r' in key or '\0' in key:
        raise ValueError(
            "Header name must not contain control characters: %r" % key)
    return key.title().replace('_', '-')


def hval(value):
    value = touni(value)
    if '\n' in value or '\r' in value or '\0' in value:
        raise ValueError(
            "Header value must not contain control characters: %r" % value)
    return value


class Singleton(type):

    _instances: Mapping[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MultiDict(UserDict):
    """ This dict stores multiple values per key, but behaves exactly like a
        normal dict in that it returns only the newest value for any given key.
        There are special methods available to access the full list of values.
    >>> d = MultiDict(a=[0], b=[1])
    >>> d == {'a': [0], 'b': [1]}
    True
    >>> len(d)
    2
    >>> d['a']
    0
    >>> d['b'] = 2
    >>> d.get('b')
    2
    >>> d.get('c', 3)
    3
    >>> d.update(b=4, c=5)
    >>> d == {'b': [1, 2, 4], 'a': [0], 'c': [5]}
    True
    """

    def __init__(self, *a, **k):
        """TODO
        """
        # self.data = {k: [v] for (k, v) in dict(*a, **k).items()}
        self.data = dict(*a, **k)

    def __getitem__(self, key):
        return self.data[key][-1]

    def __setitem__(self, key, value):
        self.data.setdefault(key, []).append(value)

    def __eq__(self, other):
        """values order is not important"""
        return dict(self.data.items()) == dict(self.data.items())

    def values(self):
        return (v[-1] for v in self.data.values())

    def items(self):
        return ((k, v[-1]) for k, v in self.data.items())

    def allitems(self):
        return ((k, v) for k, vl in self.data.items() for v in vl)

    def get(self, key, default=None, index=-1):
        try:
            val = self.data[key][index]
        except (KeyError, IndexError):
            val = default
        return val

    def get_all(self, key):
        return self.data.get(key, None) or []

    def update(self, iterable=None, **k_v):
        if iterable and issubclass(iterable, Iterable):
            for key, value in iterable:
                self.data.setdefault(key, []).append(value)
        for key, value in k_v.items():
            self.data.setdefault(key, []).append(value)


class HeaderDict(MultiDict):
    """ A case-insensitive version of :class:`MultiDict` that defaults to
        replace the old value instead of appending it.
    >>> d = HeaderDict(a=0, b=1)
    >>> d == {'a': [0], 'b': [1]}
    True
    """

    def __init__(self, *a, **k):
        """TODO
        """
        self.data = {hkey(k): [v] for (k, v) in dict(*a, **k).items()}

    def __contains__(self, key):
        return super().__contains__(hkey(key))

    def __delitem__(self, key):
        return super().__delitem__(hkey(key))

    def __getitem__(self, key):
        return super().__getitem__(hkey(key))

    def __setitem__(self, key, value):
        return super().__setitem__(hkey(key), hval(value))

    def get(self, key, default=None, index=-1):
        return super().get(hkey(key), default, index)

    def get_all(self, key):
        return super().get_all(hkey(key))


class LRUCache:
    """ LRUCache implemented with HashMap and LinkList
    >>> cache = LRUCache(3)
    >>> cache.set(1,1)
    >>> cache.set(2,2)
    >>> cache.set(3,3)
    >>> cache
    capacity: 3 [(1, 1), (2, 2), (3, 3)]
    >>> cache.get(1)
    1
    >>> cache
    capacity: 3 [(2, 2), (3, 3), (1, 1)]
    >>> cache.set(4,4)
    >>> cache
    capacity: 3 [(3, 3), (1, 1), (4, 4)]
    """

    class Node:

        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.pre = None
            self.next = None

    def __init__(self, capacity):
        self.capacity = capacity
        self._head = self.Node(None, None)
        self._tail = self.Node(None, None)
        self._head.next = self._tail
        self._tail.pre = self._head
        self._map = {}

    def get(self, key):
        n = self._map.get(key, None)
        if n is not None:
            n.pre.next = n.next
            n.next.pre = n.pre
            self._append_tail(n)
            return n.value
        raise KeyError(key)

    def set(self, key, value):
        n = self._map.get(key, None)
        # n already in the map
        if n is not None:
            n.value = value
            self._map[key] = n
            n.pre.next = n.next
            n.next.pre = n.pre
            self._append_tail(n)
            return

        # n not in the map
        # check the capacity
        if len(self._map) == self.capacity:
            tmp = self._head.next
            self._head.next = self._head.next.next
            self._head.next.pre = self._head
            self._map.pop(tmp.key)
        n = self.Node(key, value)
        self._append_tail(n)
        self._map[key] = n

    def _append_tail(self, n):
        n.next = self._tail
        n.pre = self._tail.pre
        self._tail.pre.next = n
        self._tail.pre = n

    def __repr__(self):
        tmp = self._head.next
        result = []
        while tmp is not self._tail:
            result.append((tmp.key, tmp.value))
            tmp = tmp.next
        return 'capacity: {} {}'.format(self.capacity, result.__repr__())


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)
