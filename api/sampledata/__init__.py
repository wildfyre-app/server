from .decorators import register

__all__ = [
    "AlreadyRegisterd", "NotRegistered",
    "sampledata", "register"
]

default_app_config = 'sampledata.apps.sampledataConfig'


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class _SampleDataRegistry:
    def __init__(self):
        self._registry = []  # Function

    def register(self, function):
        if function in self._registry:
            raise AlreadyRegistered("This function is already registered.")
        self._registry.append(function)

    def unregister(self, function):
        try:
            self._registry.remove(function)
        except ValueError:
            raise NotRegistered("This function is not registered.")

    def is_registered(self, function):
        return function in self._registry

    @property
    def functions(self):
        return list(self._registry)


sampledata = _SampleDataRegistry()
