from ajenti.com import *
from ajenti.utils import *


class IComponent (Interface):
    def run(self):
        pass


class Component (Plugin, BackgroundWorker):
    implements(IComponent)

    name = 'unknown'
    proxy = None
    abstract = True

    def __init__(self):
        BackgroundWorker.__init__(self)

    @classmethod
    def get(cls):
        return ComponentManager.get().find(cls.name)

    def start(self):
        self.on_starting()
        BackgroundWorker.start(self)

    def stop(self):
        self.on_stopping()
        self.kill()
        self.on_stopped()

    def run(self):
        pass

    def on_starting(self):
        pass

    def on_stopping(self):
        pass

    def on_stopped(self):
        pass

    def unload(self):
        self.stop()


class ComponentManager (Plugin):
    instance = None

    @staticmethod
    def create(app):
        ComponentManager.instance = ComponentManager(app)

    @staticmethod
    def get():
        return ComponentManager.instance

    def __init__(self):
        self.components = []
        self.rescan()

    def stop(self):
        for c in self.components:
            c.stop()

    def find(self, name):
        for c in self.components:
            if c.name == name:
                return c.proxy

    def rescan(self):
        for c in self.app.grab_plugins(IComponent):
            if not c in self.components:
                self.log.debug('Registered component: ' + c.name)
                c.proxy = ClassProxy(c)
                c.start()
                self.components.append(c)
