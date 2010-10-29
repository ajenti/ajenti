from ajenti.com import *


class ClusteredPlugin(Plugin):
    abstract = True

    def root(self):
        try:
            return self.config.get('uzuri-root')
        except:
            return ''
    
    def open(self, path, mode='r'):
        return open(self.root() + path, mode)


class IClusteredConfig(Interface):
    pass
    
    
class ClusteredConfig(ClusteredPlugin):
    abstract = True
    implements(IClusteredConfig)

    name = ''
    id = ''
    files = []
    run_after = []
