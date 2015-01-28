from aj.api import *


class Service (object):
    def __init__(self, manager):
        self.id = None
        self.name = None
        self.manager = manager
        self.state = None
        self.running = None


@interface
class ServiceManager (object):
    id = None
    name = None

    def list(self):
        raise NotImplementedError

    def get(self, id):
        raise NotImplementedError

    def start(self, id):
        raise NotImplementedError

    def stop(self, id):
        raise NotImplementedError

    def restart(self, id):
        raise NotImplementedError
