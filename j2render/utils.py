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
