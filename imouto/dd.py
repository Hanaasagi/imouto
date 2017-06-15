from collections import UserDict

def caseless_pairs(seq):
    for k, v in seq:
        yield k.lower(), v

class Immutable:

    def __setitem__(self, k, v):
        raise TypeError('{} object does not support item assignment'.format(
            self.__class__.__name__))

    def update(self, E=None, **F):
        raise TypeError('{} object does not support update'.format(
            self.__class__.__name__))


class ImmutableMultiDict(Immutable, dict):

    def __getitem__(self, k):
        if k in self:
            return super().__getitem__(k)[0]

    def get(self, k, d=None):
        if k in self:
            return super().__getitem__(k)[0]
        return d

    def get_all(self, k, d=None):
        if k in self:
            return super().__getitem__(k)
        return d

class CaselessDict(dict):

    def __init__(self, it=None, **kwargs):
        it = caseless_pairs(it) if it else []
        if kwargs:
            kwargs = {k.lower(): v for k, v in kwargs.items()}
        super().__init__(it, **kwargs)

    def __contains__(self, k):
        return super().__contains__(k.lower())

    def __getitem__(self, k):
        return super().__getitem__(k.lower())

    def __iter__(self):
        def iterator():
            for k in iter(super()):
                yield k.lower()
        return iterator()

    def __setitem__(self, k, v):
        super().__setitem__(k.lower(), v)

    def get(self, k, d=None):
        if k in self:
            return super().__getitem__(k.lower())
        return d

    def update(self, other=None, **kwargs):
        updates = {k.lower(): v for k, v in kwargs.items()}
        if other:
            if hasattr(other, 'items'):
                other = other.items()
            updates.update(caseless_pairs(other))
        return super().update(udpates)


class ImmutableCaselessDict(Immutable, CaselessDict):
    pass


class ImmutableCaselessMultiDict(ImmutableMultiDict, CaselessDict):

    def __init__(self, it=None, **kwargs):
        it = caseless_pairs(it) if it else []
        if kwargs:
            kwargs = {k.lower(): [v] for k, v in kwargs.items()}

        for k, v in it:
            if k in kwargs:
                kwargs[k].append(v)
            else:
                kwargs[k] = [v]

        super().__init__(**kwargs)


