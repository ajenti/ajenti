from aj.api.di import *


class PluginInfo:
    """
    Describes a loaded plugin package
    """

    def __init__(self, **kwargs):
        self.name = ''
        self.description = ''
        self.icon = None
        self.author = ''
        self.homepage = ''
        self.dependencies = []

        def init():
            pass

        self.init = init

        for k in kwargs:
            setattr(self, k, kwargs[k])

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __hash__(self):
        return hash(self.name)


__all__ = [
    'PluginInfo',
    'Context',
    'component',
    'interface',
    'service',
]
