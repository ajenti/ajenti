import sys


class MetaAPI(type):
    def __new__ (mcs, name, bases, d):
        new_class = type.__new__(mcs, name, bases, d)
        setattr(sys.modules[__name__], name.lower(), new_class)
        return new_class


class API(object):
    __metaclass__ = MetaAPI
