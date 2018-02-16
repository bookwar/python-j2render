import os
import yaml
import logging


def set_nested_value(dictionary, keys, value):
    '''Set nested value in the dictionary'''

    d = dictionary
    for key in keys:
        d = d.setdefault(key, {})
    d.update(value)

def get_nested_value(dictionary, keys):
    '''Get nested value from the dictionary

    Return None if there is no such key sequence.'''

    d = dictionary

    for key in keys:
        d = d.get(key, None)
        if not d:
            return None

    return d

def read_yaml_tree(path):
    '''Read YAML from a directory tree

    For each subdirectory create a key in the dictionary.
    For each .yaml file in the directory,
    if its name starts with the digit - add YAML data from file to the subdirectory key,
    else add filename as a key, and then add YAML data from file under this key.

    Example:

    ```
    - somedir/
        - 00_defaults.yaml:
              default_parameter: default_value
              another_parameter: another_default_value
        - 50_service.yaml:
              another_parameter: service_value
        - data.yaml:
              data_parameter: somevalue
    ```

    Produces:
    ```
    somedir:
      default_parameter: default_value
      another_parameter: service_value
      data:
        data_parameter: somevalue
    ```

    '''

    data = {}
    walk = os.walk(path)

    for curdir, subdirs, files in walk:
        for filename in sorted(files):
            logging.debug("Parsing {0}".format(filename))

            if not filename.endswith(".yaml"):
                logging.warning("Skipped {0} because it doesn't end with .yaml".format(filename))
                continue

            with open(os.path.join(curdir, filename)) as fd:
                filedata = yaml.load(fd)

            if not filedata:
                logging.warning("Skipped {0} as there is no data".format(filename))
                continue

            keys = os.path.relpath(curdir, path).split(os.path.sep)

            if not filename.startswith(tuple(map(str, range(10)))):
                # filename doesn't start with digit
                # use filename as a dictionary key
                keys.append(os.path.splitext(filename)[0])

            set_nested_value(data, keys, value=filedata)

    return data


class ParamTree():
    PATHS = {
        'default': [
            '_default/_global',
        ],
        'target': [
            '_default/_global',
            '{target}/_global',
        ],
        'resource': [
            'default/{resource}/_common',
            '{target}/{resource}/_common',
        ],
        'item': [
            'default/{resource}/_common',
            '{target}/{resource}/_common',
            'default/{resource}/{item}',
            '{target}/{resource}/{item}',
        ],
    }

    def __init__(self, fileroot=None, raw=None):
        if not raw:
            raw = read_yaml_tree(fileroot)

        self.raw = raw
        self.targets = [item for item in self.raw.keys() if not item.startswith("/")]

    def _get_params(self, paths=None, scope=None, **kwargs):

        data = {}

        if not paths:
            paths = self.PATHS[scope]

        for path in paths:
            value = get_nested_value(
                self.raw,
                path.format(**kwargs).split("/")
            )
            if value:
                data.update(value)

        return data

    def get_target_params(self, target):
        return self._get_params(scope='target', target=target)

    def get_item_params(self, target, resource, item):
        return self._get_params(scope='item', target=target, resource=resource, item=item)

    def get_resources(self, target=None, targets=None):
        '''List all resources mentioned in the parameter tree'''
        if target:
            targets = [target]

        if not targets:
            # If target is not specified - read all
            targets = self.targets

        resources = []
        for target in targets:
            resources += [item for item in self.raw[target].keys() if not item.startswith("_")]

        if '_default' in self.raw.keys():
            resources += [item for item in self.raw["_default"].keys() if not item.startswith("_")]

        return resources
