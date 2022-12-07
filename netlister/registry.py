class Registry(dict):
    def add(self, key, object):
        self[key] = object

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]

class RegistryMixin:
    def __init__(self, registry : Registry) -> None:
        self.registry = registry

    def __getattr__(self, attr):
        return self.registry[attr]
