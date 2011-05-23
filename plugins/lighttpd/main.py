import os

from ajenti.utils import *
from ajenti.api import *
from ajenti.com import *
from ajenti import apis


class LighttpdBackend(Plugin):
    implements(IConfigurable)
    config_dir = ''
    name = 'lighttpd'
    id = 'lighttpd'
    icon = '/dl/webserver_common/icon.png'
    
    def __init__(self):
        self.config_dir = self.app.get_config(self).cfg_dir
        if not os.path.exists(self.config_dir):
            raise ConfigurationError('Config directory does not exist') 
        
    def list_files(self):
        return [self.config_dir + '/*', self.config_dir + '/*/*']
        
    def get_mods(self):
        r = {}
        dir_conf_avail = self.config_dir + '/conf-available/'
        for h in os.listdir(dir_conf_avail):
            if not h.endswith('conf'):
                continue
            h = h.split('.')[0]
            mod = apis.webserver.Module()
            mod.name = h
            mod.has_config = True
            mod.config = open(os.path.join(self.config_dir, 'conf-available', h+'.conf')).read()
            mod.enabled = os.path.exists(
                            os.path.join(self.config_dir, 'conf-enabled', h+'.conf')
                           )
            r[h] = mod
        return r
        
    def enable_mod(self, id):
        p = os.path.join(self.config_dir, 'conf-enabled', id)
        if not os.path.exists(p+'.conf'):
            ps = os.path.join(self.config_dir, 'conf-available', id+'.conf')
            os.symlink(ps, p+'.conf')

    def disable_mod(self, id):
        p = os.path.join(self.config_dir, 'conf-enabled', id)
        if os.path.exists(p+'.conf'):
            os.unlink(p+'.conf')

    def save_mod(self, mod):
        path = os.path.join(self.config_dir, 'conf-available', mod.name+'.conf')  
        open(path, 'w').write(mod.config)
          

class LighttpdPlugin(apis.webserver.WebserverPlugin):
    text = 'lighttpd'
    icon = '/dl/lighttpd/icon.png'
    folder = 'servers'
    ws_service = 'lighttpd'
    ws_name = 'lighttpd'
    ws_icon = '/dl/lighttpd/icon.png'
    ws_title = 'lighttpd'
    ws_backend = LighttpdBackend
    ws_mods = True
    ws_vhosts = False
    
