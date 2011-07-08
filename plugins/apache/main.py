import os
import glob

from ajenti.api import *
from ajenti.com import *
from ajenti import apis


class ApacheBackend(Plugin):
    implements(IConfigurable)
    config_dir = ''
    name = 'Apache'
    id = 'apache'
    icon = '/dl/webserver_common/icon.png'
    
    def __init__(self):
        self.config_dir = self.app.get_config(self).cfg_dir
    
    def list_files(self):
        return [self.config_dir + '/*', self.config_dir + '/*/*']
        
    def get_hosts(self):
        r = {}
        for h in os.listdir(os.path.join(self.config_dir, 'sites-available')):
            data = ConfManager.get().load('apache', os.path.join(self.config_dir, 'sites-available', h))
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
            ConfManager.get().commit('apache')

    def disable_host(self, id):
        p = os.path.join(self.config_dir, 'sites-enabled', id)
        if os.path.exists(p):
            os.unlink(p)
            ConfManager.get().commit('apache')

    def delete_host(self, id):
        p = os.path.join(self.config_dir, 'sites-available', id)
        os.unlink(p)
        ConfManager.get().commit('apache')

    def save_host(self, host):
        path = os.path.join(self.config_dir, 'sites-available', host.name)  
        ConfManager.get().save('apache', path, host.config)
        ConfManager.get().commit('apache')
                  
    def get_mods(self):
        r = {}
        dir_mods_avail = self.config_dir + '/mods-available/'
        lst = [s.replace(dir_mods_avail, '').replace('.load', '') 
             for s in glob.glob(dir_mods_avail + '*.load')]
        for h in lst:
            mod = apis.webserver.Module()
            mod.name = h
            confpath = os.path.join(self.config_dir, 'mods-available', h+'.conf')
            mod.has_config = os.path.exists(confpath)
            if mod.has_config:
                mod.config = ConfManager.get().load('apache', os.path.join(self.config_dir, 'mods-available', h+'.conf'))
            mod.enabled = os.path.exists(
                            os.path.join(self.config_dir, 'mods-enabled', h+'.load')
                           )
            r[h] = mod
        return r
        
    def enable_mod(self, id):
        p = os.path.join(self.config_dir, 'mods-enabled', id)
        if not os.path.exists(p+'.load'):
            ps = os.path.join(self.config_dir, 'mods-available', id+'.load')
            os.symlink(ps, p+'.load')
        if not os.path.exists(p+'.conf'):
            if os.path.exists(os.path.join(self.config_dir, 'mods-available', id+'.conf')):
                ps = os.path.join(self.config_dir, 'mods-available', id+'.conf')
                os.symlink(ps, p+'.conf')
        ConfManager.get().commit('apache')

    def disable_mod(self, id):
        p = os.path.join(self.config_dir, 'mods-enabled', id)
        if os.path.exists(p+'.load'):
            os.unlink(p+'.load')
        if os.path.exists(p+'.conf'):
            os.unlink(p+'.conf')
        ConfManager.get().commit('apache')

    def save_mod(self, mod):
        path = os.path.join(self.config_dir, 'mods-available', mod.name+'.conf')  
        ConfManager.get().save('apache', path, mod.config)
        ConfManager.get().commit('apache')
     
    host_template = """
# %s
<VirtualHost *:80>
	ServerAdmin webmaster@localhost

	DocumentRoot /dev/null
	<Directory />
		Options FollowSymLinks
		AllowOverride None
	</Directory>
	<Directory /dev/null>
		Options Indexes FollowSymLinks MultiViews
		AllowOverride None
		Order allow,deny
		allow from all
	</Directory>

	ErrorLog ${APACHE_LOG_DIR}/error.log
	LogLevel warn
	CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
"""
                       
class ApachePlugin(apis.webserver.WebserverPlugin):
    platform = ['debian', 'arch', 'freebsd']
    text = 'Apache 2'
    icon = '/dl/apache/icon.png'
    folder = 'servers'
    ws_service = 'apache2'
    ws_name = 'apache'
    ws_icon = '/dl/apache/icon.png'
    ws_title = 'Apache 2'
    ws_backend = ApacheBackend
    ws_mods = True
    
