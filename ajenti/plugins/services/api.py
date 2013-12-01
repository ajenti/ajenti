from ajenti.api import *
from ajenti.util import cache_value


@plugin
@persistent
class ServiceMultiplexor (object):
    """
    Merges together output of all available ServiceManagers.
    """
    def init(self):
        self.managers = ServiceManager.get_all()

    @cache_value(1)
    def get_all(self):
        """
        Returns all :class:`Service` s.
        """
        r = []
        for mgr in self.managers:
            r += mgr.get_all()
        return r

    def get_one(self, name):
        """
        Returns a :class:`Service` by name.
        """
        for mgr in self.managers:
            s = mgr.get_one(name)
            if s:
                return s
        return None


@interface
@persistent
class ServiceManager (object):
    def get_all(self):
        return []

    def get_one(self, name):
        """
        Returns a :class:`Service` by name.
        """
        for s in self.get_all():
            if s.name == name:
                return s
        return None


class Service (object):
    source = 'unknown'
    """ Marks which ServiceManager owns this object """

    def __init__(self):
        self.name = None
        self.running = False

    @property
    def icon(self):
        return 'play' if self.running else None

    def start(self):
        pass

    def stop(self):
        pass

    def restart(self):
        pass

    def command(self, cmd):
        pass
