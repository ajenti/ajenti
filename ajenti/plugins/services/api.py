from ajenti.api import *


@interface
class ServiceManager (object):
    def get_all(self):
        return []

    def start(self, service):
        pass

    def stop(self, service):
        pass

    def restart(self, service):
        pass


class Service (object):
    def __init__(self):
        self.name = None
        self.running = False

    @property
    def icon(self):
        return 'play' if self.running else None
