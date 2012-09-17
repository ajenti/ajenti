__all__ = ['PluginInfo', 'plugin', 'interface']

from ajenti.plugins import manager 


class PluginInfo:
    def __init__(self, **kwargs):
        self.author = ''
        self.homepage = ''
        self.dependencies = []
        for k in kwargs:
            setattr(self, k, kwargs[k])


def plugin(cls):
    manager.register_implementation(cls)
    return cls


def interface(cls):
    manager.register_interface(cls)
    return cls