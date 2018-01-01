import os
import types
import importlib
from itertools import chain
from operator import methodcaller
from collections import UserDict
from imouto.errors import ConfigError


class ConfigAttribute:
    """ Makes an attribute forward to the config """

    def __init__(self, name, get_converter=None):
        self.__name__ = name
        self.get_converter = get_converter

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        rv = obj.config[self.__name__]
        if self.get_converter is not None:
            rv = self.get_converter(rv)
        return rv

    def __set__(self, obj, value):
        obj.config[self.__name__] = value


class Config(UserDict):

    def __init__(self, root_path=None, defaults=None):
        self.data = dict(defaults or {})
        self._root_path = root_path

    @property
    def root_path(self):
        if self._root_path is None:
            raise ConfigError("set the root_path first")
        return self._root_path

    @root_path.setter  # type: ignore
    def set_root_path(self, path):
        self._root_path = path

    def from_object(self, obj):
        """ Update the values from the given object.
        Objects are usually either modules or classes.
        """
        for key in dir(obj):
            if key.isupper():
                self.data[key] = getattr(obj, key)

    def from_envvar(self, variable_name: str) -> bool:
        """ Load a configuration from an environment variable pointing to
        a configuration file.
        """
        rv: str = os.environ.get(variable_name)
        if not rv:
            raise RuntimeError('The environment variable %r is not set '
                               'and as such configuration could not be '
                               'loaded.  Set this variable and make it '
                               'point to a configuration file' %
                               variable_name)
        return self.from_pyfile(rv)

    def from_pyfile(self, filename: str) -> bool:
        """ Update the values in the config from a Python file.
        Only the uppercase variables in that module are stored in the config.
        """
        filename = os.path.join(self.root_path, filename)
        module = types.ModuleType('config')
        module.__file__ = filename
        try:
            with open(filename, 'r') as config_file:
                exec(compile(config_file.read(), filename, 'exec'),
                     module.__dict__)
        except IOError as e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(module)
        return True

    def from_yaml(self, filename: str) -> bool:
        """ Update the values from a yaml file. """
        try:
            yaml = importlib.import_module('yaml')
        except ModuleNotFoundError as e:
            e.msg = ('Unable to load configuration file '  # type: ignore
                     '(%s)') % e.msg  # type: ignore
            raise
        filename = os.path.join(self.root_path, filename)
        try:
            with open(filename, 'r') as yaml_file:
                obj = yaml.loads(yaml_file.read())  # type: ignore
        except IOError as e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        return self.from_mapping(obj)

    def from_toml(self, filename: str) -> bool:
        """ Update the values from a toml file. """
        try:
            toml = importlib.import_module('toml')
        except ModuleNotFoundError as e:
            e.msg = ('Unable to load configuration file '  # type: ignore
                     '(%s)') % e.msg  # type: ignore
            raise
        filename = os.path.join(self.root_path, filename)
        try:
            with open(filename, 'r') as toml_file:
                obj = toml.loads(toml_file.read())  # type: ignore
        except IOError as e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        return self.from_mapping(obj)

    def from_json(self, filename: str) -> bool:
        """ Updates the values in the config from a JSON file. """
        try:
            json = importlib.import_module('toml')
        except ModuleNotFoundError as e:
            e.msg = ('Unable to load configuration file '  # type: ignore
                     '(%s)') % e.msg  # type: ignore
            raise
        filename = os.path.join(self.root_path, filename)
        try:
            with open(filename, 'r') as json_file:
                obj = json.loads(json_file.read())  # type: ignore
        except IOError as e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        return self.from_mapping(obj)

    def from_mapping(self, *mapping, **kwargs) -> bool:
        """ Updates the config like :meth:`update` but ignoring items with
        non-upper keys.
        """
        if len(mapping) > 1:
            raise TypeError(
                'expected at most 1 positional argument, got %d' % len(mapping)
            )
        dict_: dict = {}
        if len(mapping) == 1:
            dict_ = mapping[0]
            if not isinstance(dict_, dict):
                raise TypeError(
                    'expected dict type argument, got %s' % dict_.__class__
                )

        for key, value in chain(*map(methodcaller('items'),
                                     (dict_, kwargs))):
            if key.isupper():
                self.data[key] = value
        return True

    def get_namespace(self, namespace, lowercase=True, trim_namespace=True):
        """ Returns a dict containing a subset of configuration options """
        rv = {}
        for k, v in self.data.items():
            if not k.startswith(namespace):
                continue
            key = k[len(namespace):] if trim_namespace else k
            if lowercase:
                key = key.lower()
            rv[key] = v
        return rv

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self.data))
