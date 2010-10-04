from ajenti.com import *


class IClusteredConfig(Interface):
    pass
    
    
class ClusteredConfig(Plugin):
    abstract = True
    implements(IClusteredConfig)

    name = ''
    id = ''
    files = []
    run_after = []
    
    def root(self):
        try:
            return self.config.get('uzuri-root')
        except:
            return ''
    
    def open(self, path, mode='r'):
        return open(self.root() + path, mode)
