from ajenti.com import *
from ajenti.utils import *
from ajenti import apis

import os
import re
import glob


class ApacheSingleConfigBackend(Plugin):
    config_dir = ''
    name = 'Apache'
    id = 'apache'
    
    def __init__(self):
        self.config_path = self.app.get_config(self).cfg_file
        if not os.path.exists(self.config_path):
            raise ConfigurationError('Can\'t find config file') 

    def get_hosts(self):
        r = {}
        f = open(self.config_path)
        text = f.read()
        pat = re.compile('<VirtualHost (.+?:\d+)>',re.S)
        for m in pat.finditer(text):
            beg = m.start()
            while(text[beg] != '\n' and beg > 0):
                beg = beg - 1
            enabled = not (text[beg + 1] == '#')
            item = apis.webserver.VirtualHost()
            item.name = str(m.group(1))
            item.enabled = enabled
            
            if(enabled):
                pat_in = re.compile('(.+?)[^#]\s*</VirtualHost>', re.S)
            else:
                pat_in = re.compile('(.+?)#\s*</VirtualHost>', re.S)
                
            data = pat_in.search(text, beg)
            if(not data):
                continue
            data = data.group()
            data = data.replace('\n#','\n')
            item.config = re.sub('#.+?\n','',data)
            r[item.name] = item
        f.close()
        return r

    def save_host(self, host):
        id = host.name
        id = id.replace('*','\*')
        id = id.replace('.','\.')
    
        f = open(self.config_path, 'r')
        text = f.read()
        f.close()
    
        pat = re.compile('(?:#\s*)*<VirtualHost ' + id + '>(.+?)</VirtualHost>', re.S)
        res = pat.search(text)
    
        if res:
            host_text = host.config
            host_text = host_text.replace('\n', '\n#')
            host_text = '#' + host_text
            text = text.replace(res.group(0), host_text)
            f = open(self.config_path, 'w')
            f.write(text)
            f.close()
        else:    
            f = open(self.config_path, 'a+')
            f.write('\n\n' + host.config)
            f.close()

    def delete_host(self, id):
        id = id.replace('*','\*')
        id = id.replace('.','\.')
        f = open(self.config_path, 'r')
        text = f.read()
        f.close()
        
        text = repl_pat.sub('', text)
        f = open(self.config_path, 'w')
        f.write(text)
        f.close()

    def disable_host(self, id):
        id = id.replace('*','\*')
        id = id.replace('.','\.')
        f = open(self.config_path, 'r')
        text = f.read()
        f.close()
        pat = re.compile('(?:#\s*)*<VirtualHost ' + id + '>(.+?)</VirtualHost>', re.S)
        res = pat.search(text)
        host_text = res.group(0)
        host_text = host_text.replace('\n', '\n#')
        host_text = '#' + host_text
        text = text.replace(res.group(0), host_text)
        f = open(self.config_path, 'w')
        f.write(text)
        f.close()

    def enable_host(self, id):
        id = id.replace('*','\*')
        id = id.replace('.','\.')
        f = open(self.config_path, 'r')
        text = f.read()
        f.close()
        pat = re.compile('#\s*<VirtualHost ' + id + '>(.+?)#\s*</VirtualHost>', re.S)
        res = pat.search(text)
        host_text = res.group(0)
        host_text = host_text.replace('\n#', '\n')
        host_text = host_text[1:]
        text = text.replace(res.group(0), host_text)
        f = open(self.config_path, 'w')
        f.write(text)
        f.close()
        

          
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
                mod.config = open(os.path.join(self.config_dir, 'mods-available', h+'.conf')).read()
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

    def disable_mod(self, id):
        p = os.path.join(self.config_dir, 'mods-enabled', id)
        if os.path.exists(p+'.load'):
            os.unlink(p+'.load')
        if os.path.exists(p+'.conf'):
            os.unlink(p+'.conf')

    def save_mod(self, mod):
        path = os.path.join(self.config_dir, 'mods-available', mod.name+'.conf')  
        open(path, 'w').write(mod.config)
     
    host_template = """
<VirtualHost %s>
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
                       
class ApacheSCPlugin(apis.webserver.WebserverPlugin):
    platform = [] # <-- TODO put stuff here
    text = 'Apache 2'
    icon = '/dl/apache/icon.png'
    folder = 'servers'
    ws_service = 'apache2'
    ws_name = 'apache'
    ws_icon = '/dl/apache/icon.png'
    ws_title = 'Apache 2'
    ws_backend = ApacheSingleConfigBackend
    ws_mods = True
