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
            
    def _clean(self, data):
        lines = data.split('\n')
        r = []
        for l in lines:
            l = l.split()
            if len(l) > 0:
                for x in l:
                    if not x.startswith('#'):
                        r.append(x)
                    else:
                        break
        return r
        
    def _parse_host(self, data):
        data = self._clean(data)[2:-1]
        h = apis.webserver.VirtualHost()
        while len(data) > 0:
            key = data[0]
            
            value = []
            data = data[1:]
            while len(data)>0 and not data[0] in [';', '{']:
                if data[0].endswith(';'):
                    value.append(data[0][:-1])
                    data[0] = ';'
                    break
                else:
                    value.append(data[0])
                    data = data[1:]
            value = ' '.join(value)
            
            if data[0] == ';':
                data = data[1:]
                if key == 'listen':
                    h.names.append(value)
                elif key == 'server_name':
                    h.servername = value
                elif key == 'ssl':
                    h.ssl = value == 'on'
                elif key == 'ssl_certificate':
                    h.ssl_cert = value
                elif key == 'ssl_certificate_key':
                    h.ssl_key = value
                else:
                    h.params.append((key, value))
            else:
                if key == 'location':
                    data, loc = self._parse_location(data)
                    loc.name = value
                    h.locations.append(loc)
        return h
    
    def _parse_location(self, data):
        data = data[1:]
        loc = apis.webserver.Location()
                
        while not data[0] == '}':
            loc.params += data[0]
            if data[0].endswith(';'):
                loc.params += '\n' 
            else:
                loc.params += ' ' 
            data = data[1:]
        data = data[1:]
        return data, loc
        
        
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
