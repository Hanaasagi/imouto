from collections import UserDict, Iterable
from httputil import _hkey, _hval


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
        return super().__contains__(_hkey(key))

    def __delitem__(self, key):
        return super().__delitem__(_hkey(key))

    def __getitem__(self, key):
        return super().__getitem__(_hkey(key))

    def __setitem__(self, key, value):
        return super().__setitem__(_hkey(key), _hval(value))

    def getall(self, key):
        return super().getall(_hkey(key))

    def get(self, key, default=None, index=-1):
        return super().get(self, _hkey(key), default, index)
