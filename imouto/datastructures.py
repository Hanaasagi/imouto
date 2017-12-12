from collections import UserDict, Iterable
from imouto.utils import hkey, hval


class ImmutableDict(UserDict):
    _hash_cache = None

    def __init__(*args, **kwargs):
        if not args:
            raise TypeError("descriptor '__init__' of 'UserDict' object "
                            "needs an argument")
        self, *args = args
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        if args:
            dict_ = args[0]
        elif 'dict' in kwargs:
            dict_ = kwargs.pop('dict')
            import warnings
            warnings.warn("Passing 'dict' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        else:
            dict_ = None
        self.data = {}
        if dict_ is not None:
            self.data.update(dict_)
        if len(kwargs):
            self.data.update(kwargs)

    def __hash__(self):
        """ Hash should be same """
        if self._hash_cache is not None:
            return self._hash_cache
        self._hash_cache = rv = hash(frozenset(self.data.items()))
        return rv

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            dict.__repr__(self.data),
        )

    def copy(self):
        """ Return a shallow mutable copy of this object.  Keep in mind that
        the standard library's :func:`copy` function is a no-op for this class
        like for any other python immutable type (eg: :class:`tuple`).
        """
        return dict(self.data)

    def __copy__(self):
        return self.__class__(self.data)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d.data[key] = value
        return d

    def complain(self, *args, **kwargs):
        raise TypeError('%r objects are immutable' % self.__class__.__name__)

    setdefault = complain
    update = complain
    pop = complain
    popitem = complain
    __setitem__ = complain
    __delitem__ = complain
    clear = complain


class ConstantsObject(ImmutableDict):

    def __getattr__(self, name):
        return self.data[name]

    def __dir__(self):
        return self.data.keys()


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


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)
