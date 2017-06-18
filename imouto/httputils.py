from collections import UserDict, Iterable

"""Some utility functions and classes"""


def trim_keys(dict_):
    """remove dict keys with leading and trailing whitespace
    """
    return {k.strip(): v for k, v in dict_.items()}


def tob(s, enc='utf8'):
    """convert to bytes
    """
    return s.encode(enc) if isinstance(s, str) else bytes(s)


def touni(s, enc='utf8', err='strict'):
    """convert to unicode
    """
    return s.decode(enc, err) if isinstance(s, bytes) else str(s)


def hkey(key):
    if '\n' in key or '\r' in key or '\0' in key:
        raise ValueError("Header names must not contain control characters: %r" % key)
    return key.title().replace('_', '-')


def hval(value):
    value = touni(value)
    if '\n' in value or '\r' in value or '\0' in value:
        raise ValueError("Header value must not contain control characters: %r" % value)
    return value


class MultiDict(UserDict):
    """ This dict stores multiple values per key, but behaves exactly like a
        normal dict in that it returns only the newest value for any given key.
        There are special methods available to access the full list of values.
    >>> d = MultiDict(a=0, b=1)
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
        self.data = dict((k, [v]) for (k, v) in dict(*a, **k).items())

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

    def getall(self, key):
        return self.data.get(key, None) or []

    def update(self, iterable=None, **k_v):
        if iterable and issubclass(iterable, Iterable):
            for key, value in iterable:
                self.data.setdefault(key, []).append(value)
        for key, value in k_v.items():
            self.data.setdefault(key, []).append(value)


class HeaderDict(MultiDict):
    """ A case-insensitive version of :class:`MultiDict` that defaults to
        replace the old value instead of appending it. """

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

    def getall(self, key):
        return super().getall(hkey(key))
