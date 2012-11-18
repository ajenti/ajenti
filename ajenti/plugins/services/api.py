from ajenti.api import *


@plugin
class ServiceMultiplexor (object):
    def init(self):
        self.managers = ServiceManager.get_all()

    def get_all(self):
        r = []
        for mgr in self.managers:
            r += mgr.get_all()
        return r


@interface
class ServiceManager (object):
    def get_all(self):
        return []


class Service (object):
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
