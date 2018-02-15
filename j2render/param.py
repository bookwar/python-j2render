from utils import read_yaml_tree, get_nested_value


class ParamTree():
    PATHS = {
        'default': [
            '_default/_global',
        ],
        'global': [
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

    def get_global_params(self, target):
        return self._get_params(scope='global', target=target)

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
