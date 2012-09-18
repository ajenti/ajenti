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
    return cls


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

    
__all__ = [
    'PluginInfo', 
    'plugin', 
    'interface',
]

