import os

from ajenti.com import *
from ajenti.app.helpers import ModuleContent
from ajenti import apis
from ajenti.plugins.uzuri_common import ClusteredConfig


class NginxBackend(ClusteredConfig):
    config_dir = '/etc/nginx/'
    name = 'nginx'
    id = 'nginx'
    files = [('/etc/nginx', '*')] 
    run_after = ['service nginx restart']
    
    def is_installed(self):
        return os.path.exists(self.root()+self.config_dir)
        
    def get_hosts(self):
        r = {}
        for h in os.listdir(os.path.join(self.root()+self.config_dir, 'sites-available')):
            data = self.open(os.path.join(self.config_dir, 'sites-available', h)).read()
            host = apis.webserver.VirtualHost()
            host.config = data
            host.name = h
            host.enabled = os.path.exists(
                            os.path.join(self.root()+self.config_dir, 'sites-enabled', h)
                           )
            r[h] = host
        return r
        
    def enable_host(self, id):
        p = os.path.join(self.root()+self.config_dir, 'sites-enabled', id)
        if not os.path.exists(p):
            ps = os.path.join(self.root()+self.config_dir, 'sites-available', id)
            os.symlink(ps, p)

    def disable_host(self, id):
        p = os.path.join(self.root()+self.config_dir, 'sites-enabled', id)
        if os.path.exists(p):
            os.unlink(p)

    def delete_host(self, id):
        p = os.path.join(self.root()+self.config_dir, 'sites-available', id)
        os.unlink(p)
        
    def save_host(self, host):
        path = os.path.join(self.config_dir, 'sites-available', host.name)  
        self.open(path, 'w').write(host.config)
          
    host_template = """
server {
	listen 80;
	server_name localhost;
	access_log /var/log/nginx/localhost.access.log;

	location / {
		root /dev/null;
		index index.html index.htm;
	}
}"""                      
 
                  
class NginxPlugin(apis.webserver.WebserverPlugin):
    text = 'nginx'
    icon = '/dl/nginx/icon_small.png'
    folder = 'servers'
    ws_service = 'nginx'
    ws_name = 'nginx'
    ws_icon = '/dl/nginx/icon.png'
    ws_title = 'nginx'
    ws_backend = NginxBackend


class NginxContent(ModuleContent):
    module = 'nginx'
    path = __file__
