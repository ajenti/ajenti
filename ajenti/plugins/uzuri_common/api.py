from ajenti.com import *


class IClusteredConfig(Interface):
    pass
    
    
class ClusteredConfig(Plugin):
    abstract = True
    implements(IClusteredConfig)

    name = ''
    id = ''
    files = []
        
    def root(self):
        try:
            return self.config.get('uzuri-root')
        except:
            return ''
    
    def open(self, path, mode='r'):
        return open(self.root() + path, mode)
