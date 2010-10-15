import os

from ajenti.com import *
from ajenti.app.helpers import ModuleContent
from ajenti import apis
from ajenti.plugins.uzuri_common import ClusteredConfig


class LighttpdBackend(ClusteredConfig):
    config_dir = '/etc/lighttpd/'
    name = 'lighttpd'
    id = 'lighttpd'
    files = [('/etc/lighttpd', '*')] 
    run_after = ['service lighttpd restart']
    
    def is_installed(self):
        return os.path.exists(self.root()+self.config_dir)
 
    def get_mods(self):
        r = {}
        dir_conf_avail = self.root()+self.config_dir + '/conf-available/'
        for h in os.listdir(dir_conf_avail):
            if not h.endswith('conf'):
                continue
            h = h.split('.')[0]
            mod = apis.webserver.Module()
            mod.name = h
            mod.has_config = True
            mod.config = self.open(os.path.join(self.config_dir, 'conf-available', h+'.conf')).read()
            mod.enabled = os.path.exists(
                            os.path.join(self.root()+self.config_dir, 'conf-enabled', h+'.conf')
                           )
            r[h] = mod
        return r
        
    def enable_mod(self, id):
        p = os.path.join(self.root()+self.config_dir, 'conf-enabled', id)
        if not os.path.exists(p+'.conf'):
            ps = os.path.join(self.root()+self.config_dir, 'conf-available', id+'.conf')
            os.symlink(ps, p+'.conf')

    def disable_mod(self, id):
        p = os.path.join(self.root()+self.config_dir, 'conf-enabled', id)
        if os.path.exists(p+'.conf'):
            os.unlink(p+'.conf')

    def save_mod(self, mod):
        path = os.path.join(self.config_dir, 'conf-available', mod.name+'.conf')  
        self.open(path, 'w').write(mod.config)
          

class LighttpdPlugin(apis.webserver.WebserverPlugin):
    text = 'lighttpd'
    icon = '/dl/lighttpd/icon_small.png'
    folder = 'servers'
    ws_service = 'lighttpd'
    ws_name = 'lighttpd'
    ws_icon = '/dl/lighttpd/icon.png'
    ws_title = 'lighttpd'
    ws_backend = LighttpdBackend
    ws_mods = True
    ws_vhosts = False
    
    
class LighttpdContent(ModuleContent):
    module = 'lighttpd'
    path = __file__
    
