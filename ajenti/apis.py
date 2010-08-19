import sys

from ajenti.app.api import *


class MetaAPI(type):
    def __new__ (cls, name, bases, d):
        new_class = type.__new__(cls, name, bases, d)
        setattr(sys.modules[__name__], name.lower(), new_class)
        return new_class


class API(object):
    __metaclass__ = MetaAPI
