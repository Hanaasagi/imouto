from collections import UserDict


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
