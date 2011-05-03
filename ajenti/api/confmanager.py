from ajenti.com import Interface, implements
from ajenti.api import *
from ajenti.apis import API
from ajenti import apis


class ConfManager (Component):
    name = 'confmanager'

    configurables = {}
        
    def load(self, id, path):
        cfg = self.get_configurable(id)
        for c in self.configurables.values():
            c.pre_load(cfg, path)
            
        with open(path, 'r') as f:
            data = f.read()
        
        for c in self.configurables.values():
            data = c.post_load(cfg, path, data)
        
        return data
        
    def save(self, id, path, data):
        cfg = self.get_configurable(id)

        for c in self.configurables.values():
            data = c.pre_save(cfg, path, data)
            
        with open(path, 'w') as f:
            f.write(data)
        
        for c in self.configurables.values():
            c.post_save(cfg, path)
        
        return data
        
    def notify_finished(self, id):
        cfg = self.get_configurable(id)
        for c in self.configurables.values():
            c.finished(cfg)
        
    def get_configurable(self, id):
        for c in self.configurables:
            if c.name == id:
                return c
        
    def on_starting(self):
        for cfg in self.app.grab_plugins(IConfigurable):
            self.log.debug('Registered configurable: ' + cfg.name)
            self.configurables[cfg.name] = cfg
        
    def on_stopping(self):
        pass
        
    def on_stopped(self):
        pass
        
    

class IConfMgrHook (Interface):
    def pre_load(self, cfg, path):
        pass
     
    def post_load(self, cfg, path, data):
        pass
            
    def pre_save(self, cfg, path, data):
        pass

    def post_save(self, cfg, path):
        pass
            
    def finished(self, cfg):
        pass
   
   
class ConfMgrHook (Plugin):
    implements(IConfMgrHook)
     
    def pre_load(self, cfg, path):
        pass
     
    def post_load(self, cfg, path, data):
        return data
            
    def pre_save(self, cfg, path, data):
        return data

    def post_save(self, cfg, path):
        pass
            
    def finished(self, cfg):
        pass
      
      
class IConfigurable (Interface):
    name = None
    id = None
       
    def list_files(self):
        pass
            
