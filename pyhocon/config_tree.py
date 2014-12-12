from pyhocon.exceptions import ConfigException, ConfigWrongTypeException, ConfigMissingException


class ConfigTree(object):
    KEY_SEP = '.'

    def __init__(self):
        self._dictionary = {}

    def _merge_config_tree(self, a, b):
        """Merge config b into a

        :param a: target config
        :type a: ConfigTree
        :param b: source config
        :type b: ConfigTree
        :return: merged config a
        """
        for key, value in b._dictionary.items():
            # if key is in both a and b and both values are dictionary then merge it otherwise override it
            if key in a._dictionary.items() and isinstance(a._dictionary[key], ConfigTree) and isinstance(a._dictionary[key], ConfigTree):
                self._merge_dict(a._dictionary[key], b._dictionary[key])
            else:
                a._dictionary[key] = value

        return a

    def _put(self, key_path, value):
        key_elt = key_path[0]
        if len(key_path) == 1:
            # if value to set does not exist, override
            # if they are both configs then merge
            # if not then override
            if key_elt in self._dictionary and isinstance(self._dictionary[key_elt], ConfigTree) and isinstance(value, ConfigTree):
                self._merge_config_tree(self._dictionary[key_elt], value)
            else:
                self._dictionary[key_elt] = value
        else:
            next_config_tree = self._dictionary.get(key_elt)
            if not isinstance(next_config_tree, ConfigTree):
                # create a new dictionary or overwrite a previous value
                next_config_tree = ConfigTree()
                self._dictionary[key_elt] = next_config_tree
            next_config_tree._put(key_path[1:], value)

    def _get(self, key_path, key_index=0):
        key_elt = key_path[key_index]
        elt = self._dictionary.get(key_elt)

        if key_index == len(key_path) - 1:
            return elt

        if elt is None:
            raise ConfigMissingException("No configuration setting found for key {key}".format(key='.'.join(key_path[:key_index + 1])))
        elif isinstance(elt, ConfigTree):
            return elt._get(key_path, key_index + 1)
        else:
            raise ConfigWrongTypeException("{key} has type {type} rather than dict".format(key='.'.join(key_path[:key_index + 1]), type=type(elt).__name__))

    def put(self, key, value):
        """Put a value in the tree (dot separated)

        :param key: key to use (dot separated). E.g., a.b.c
        :type key: basestring
        :param value: value to put
        """
        self._put(key.split(ConfigTree.KEY_SEP), value)

    def get(self, key):
        """Get a value from the tree

        :param key: key to use (dot separated). E.g., a.b.c
        :type key: basestring
        :return: value in the tree located at key
        """
        return self._get(key.split(ConfigTree.KEY_SEP))

    def get_string(self, key):
        """Return string representation of value found at key

        :param key: key to use (dot separated). E.g., a.b.c
        :type key: basestring
        :return: string value
        :type return: basestring
        """
        return str(self.get(key))

    def get_int(self, key):
        """Return int representation of value found at key

        :param key: key to use (dot separated). E.g., a.b.c
        :type key: basestring
        :return: int value
        :type return: int
        """
        return int(self.get(key))

    def get_float(self, key):
        """Return float representation of value found at key

        :param key: key to use (dot separated). E.g., a.b.c
        :type key: basestring
        :return: float value
        :type return: float
        """
        return float(self.get(key))

    def get_bool(self, key):
        """Return boolean representation of value found at key

        :param key: key to use (dot separated). E.g., a.b.c
        :type key: basestring
        :return: boolean value
        :type return: bool
        """
        return bool(self.get(key))

    def get_list(self, key):
        """Return list representation of value found at key

        :param key: key to use (dot separated). E.g., a.b.c
        :type key: basestring
        :return: list value
        :type return: list
        """
        value = self.get(key)
        if isinstance(value, list):
            return value
        else:
            raise ConfigException("{key} has type '{type}' rather than 'list'".format(key=key, type=type(value).__name__))

    def get_config(self, key):
        """Return tree config representation of value found at key

        :param key: key to use (dot separated). E.g., a.b.c
        :type key: basestring
        :return: config value
        :type return: ConfigTree
        """
        value = self.get(key)
        if isinstance(value, ConfigTree):
            return value
        else:
            raise ConfigException("{key} has type '{type}' rather than 'config'".format(key=key, type=type(value).__name__))

    def items(self):
        """Return items found in the config

        :return: list of items
        :type return: list
        """
        return self._dictionary.items()

    def iteritems(self):
        """Return items iterator found in the config

        :return: items iterator
        :type return: iterator
        """
        return self._dictionary.iteritems()

    def iterkeys(self):
        """Return keys iterator found in the config

        :return: keys iterator
        :type return: iterator
        """
        return self._dictionary.iterkeys()

    def itervalues(self):
        """Return values iterator found in the config

        :return: values iterator
        :type return: iterator
        """
        return self._dictionary.itervalues()

    def __getitem__(self, item):
        val = self.get(item)
        if val is None:
            raise KeyError(item)

        return val

    def __contains__(self, item):
        return item in self._dictionary

    def __str__(self):
        return str(self._dictionary)

    def __repr__(self):
        return repr(self._dictionary)

    def __len__(self):
        return len(self._dictionary)
