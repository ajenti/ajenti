import os

from ajenti.com import *
from ajenti.app.helpers import ModuleContent
from ajenti import apis


class NginxBackend:
    config_dir = '/etc/nginx/'
    
    def is_installed(self):
        return os.path.exists(self.config_dir)
        
    def get_hosts(self):
        r = {}
        for h in os.listdir(os.path.join(self.config_dir, 'sites-available')):
            data = open(os.path.join(self.config_dir, 'sites-available', h)).read()
            host = self._parse_host(data)
            host.enabled = os.path.exists(
                            os.path.join(self.config_dir, 'sites-enabled', h)
                           )
            r[h] = host
        return r
        
    def enable_host(self, id):
        p = os.path.join(self.config_dir, 'sites-enabled', id)
        if not os.path.exists(p):
            ps = os.path.join(self.config_dir, 'sites-available', id)
            os.symlink(ps, p)

    def disable_host(self, id):
        p = os.path.join(self.config_dir, 'sites-enabled', id)
        if os.path.exists(p):
            os.unlink(p)
            
    def _parse_host(self, data):
        h = apis.webserver.VirtualHost()
        return h
    
class NginxPlugin(apis.webserver.WebserverPlugin):
    text = 'nginx'
    icon = '/dl/nginx/icon_small.png'
    folder = 'servers'
    ws_service = 'nginx'
    ws_name = 'nginx'
    ws_icon = '/dl/nginx/icon.png'
    ws_title = 'nginx'
    ws_backend = NginxBackend()


class NginxContent(ModuleContent):
    module = 'nginx'
    path = __file__
