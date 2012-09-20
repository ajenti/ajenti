import os
import inspect

from ajenti.plugins import manager 


class PluginInfo:
    def __init__(self, **kwargs):
        self.author = ''
        self.homepage = ''
        self.dependencies = []

        def init(): 
            pass

        self.init = init
        
        for k in kwargs:
            setattr(self, k, kwargs[k])


def plugin(cls):
    manager.register_implementation(cls)
    cls._plugin = True
    cls._path = inspect.getfile(cls)
    
    def get(cls):
        return manager.get_instance(cls)
    cls.get = get.__get__(cls)
    return cls


def _check_plugin(cls):
    if not hasattr(cls, '_plugin'):
        raise Exception('Class %s must be decorated with @plugin' % cls)


def interface(cls):
    def get(cls):
        return manager.get_instance(manager.get_implementations(cls)[0])
    def get_all(cls):
        return [manager.get_instance(x) for x in manager.get_implementations(cls)]
    def get_class(cls):
        return manager.get_implementations(cls)[0]
    def get_classes(cls):
        return manager.get_implementations(cls)
    manager.register_interface(cls)
    cls.get = get.__get__(cls)
    cls.get_all = get_all.__get__(cls)
    cls.get_class = get_class.__get__(cls)
    cls.get_classes = get_classes.__get__(cls)
    return cls


class BasePlugin (object):
    def open_content(self, path, mode='r'):
        _check_plugin(self.__class__)

        root = os.path.split(self.__class__._path)[0]
        while len(root) > 1 and not os.path.exists(os.path.join(root, 'content')):
            root = os.path.split(root)[0]
        if len(root) <= 1:
            raise Exception('content directory not found')
        return open(os.path.join(root, 'content', path), mode)

    
__all__ = [
    'PluginInfo', 
    'BasePlugin',
    'plugin', 
    'interface',
]

