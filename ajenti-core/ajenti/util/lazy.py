import logging


class LazyModule (object):
    def __init__(self, module, object=None):
        self.__module = module
        self.__object = object
        self.__loaded = False

    def __load(self):
        logging.debug('Lazy-loading module %s' % self.__module)
        target = __import__(self.__module, fromlist=[''])
        if self.__object:
            target = getattr(target, self.__object)
        self.__dict__ = target.__dict__

    def __getattr__(self, attr):
        self.__load()
        return self.__dict__[attr]


