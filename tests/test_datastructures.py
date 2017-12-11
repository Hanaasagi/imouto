# flake8: noqa

import pytest
import pickle
import copy
from imouto.datastructures import *


class TestImmutableDict:

    def test_pickle(self):
        data = {'foo': 1, 'bar': 2, 'hoge': 3}
        d = ImmutableDict(data)
        s = pickle.dumps(d)
        dd = pickle.loads(s)
        assert isinstance(dd, type(d))
        assert d == dd

    def test_follows_dict_interface(self):
        data = {'foo': 1, 'bar': 2, 'hoge': 3}
        d = ImmutableDict(data)
        assert d['foo'] == 1
        assert sorted(d.keys()) == sorted(['bar', 'hoge', 'foo'])
        assert 'foo' in d
        assert 'foox' not in d
        assert len(d) == 3
        dd = ImmutableDict.fromkeys(data.keys(), 'OK')
        assert dd['foo'] == 'OK'
        assert type(dd) == ImmutableDict
        dd = d.copy()
        assert dd['foo'] == 1
        assert type(dd) == dict
        dd = copy.copy(d)
        assert dd['foo'] == 1
        assert type(dd) == ImmutableDict
        s = repr(dd)
        assert "ImmutableDict({" in s

    def test_dict_is_hashable(self):
        immutable = ImmutableDict({'a': 1, 'b': 2})
        immutable2 = ImmutableDict({'a': 2, 'b': 2})
        x = set([immutable])
        assert immutable in x
        assert immutable2 not in x
        x.discard(immutable)
        assert immutable not in x
        assert immutable2 not in x
        x.add(immutable2)
        assert immutable not in x
        assert immutable2 in x
        x.add(immutable)
        assert immutable in x
        assert immutable2 in x

    def test_immutable(self):
        data = {'foo': 1, 'bar': 2, 'hoge': 3}
        d = ImmutableDict(data)
        with pytest.raises(TypeError) as exc:
            d.clear()
        with pytest.raises(TypeError) as exc:
            d.pop('bar')
        with pytest.raises(TypeError) as exc:
            d['a'] = 1
        with pytest.raises(TypeError) as exc:
            d.setdefault('x', 1)
        with pytest.raises(TypeError) as exc:
            d.update({'foo': 2})
        with pytest.raises(TypeError) as exc:
            del d['foo']
        with pytest.raises(TypeError) as exc:
            d.popitem()
        assert exc.match('ImmutableDict') is not None


class TestConstantsObject:

    def test_getattr(self):
        data = {'foo': 1, 'bar': 2, 'hoge': 3}
        d = ConstantsObject(data)
        assert d.foo == 1

