from ajenti.com import *
from ajenti.utils import *


class IComponent (Interface):
    def run(self):
        pass
        
class Component (Plugin, BackgroundWorker):
    implements(IComponent)
    
    name = 'unknown'
    
    def __init__(self):
        BackgroundWorker.__init__(self)
    
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
        
        
class ComponentManager (Plugin):
    instance = None
    
    @staticmethod
    def create(app):
        ComponentManager.instance = ComponentManager(app)

    @staticmethod
    def get():
        return ComponentManager.instance
                
    def __init__(self):
        self.components = self.app.grab_plugins(IComponent)
        for c in self.components:
            c.start()
            c.proxy = ClassProxy(c)
            
    def stop(self):
        for c in self.components:
            c.stop()
    
    def find(self, name):
        for c in self.components:
            if c.name == name:
                return c.proxy
                
