import os

from ajenti.api import *
from ajenti.com import *
from ajenti.utils import *
from ajenti import apis


class NginxBackend(Plugin):
    implements(IConfigurable)
    config_dir = ''
    name = 'nginx'
    id = 'nginx'
    icon = '/dl/webserver_common/icon.png'
    
    def __init__(self):
        self.config_dir = self.app.get_config(self).cfg_dir
        if not os.path.exists(self.config_dir):
            raise ConfigurationError('Config directory does not exist') 

    def list_files(self):
        return [self.config_dir+'/*',self.config_dir+'/*/*']
        
    def get_hosts(self):
        r = {}
        for h in os.listdir(os.path.join(self.config_dir, 'sites-available')):
            data = ConfManager.get().load('nginx', os.path.join(self.config_dir, 'sites-available', h))
            host = apis.webserver.VirtualHost()
            host.config = data
            host.name = h
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

    def delete_host(self, id):
        p = os.path.join(self.config_dir, 'sites-available', id)
        os.unlink(p)
        
    def save_host(self, host):
        path = os.path.join(self.config_dir, 'sites-available', host.name)  
        ConfManager.get().save('nginx', path, host.config)
          
    host_template = """
server {
	listen 80;
	server_name %s;
	access_log /var/log/nginx/localhost.access.log;

	location / {
		root /dev/null;
		index index.html index.htm;
	}
}"""                      
 
                  
class NginxPlugin(apis.webserver.WebserverPlugin):
    platform = []
    text = 'nginx'
    icon = '/dl/nginx/icon.png'
    folder = 'servers'
    ws_service = 'nginx'
    ws_name = 'nginx'
    ws_icon = '/dl/nginx/icon.png'
    ws_title = 'nginx'
    ws_backend = NginxBackend
