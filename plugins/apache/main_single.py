from ajenti.api import *
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
    icon = '/dl/webserver_common/icon.png'
    
    def __init__(self):
        self.config_path = self.app.get_config(self).cfg_file
        self.config_dir = self.app.get_config(self).cfg_dir
        if not os.path.exists(self.config_path):
            raise ConfigurationError('Can\'t find config file') 

    def list_files(self):
        return [self.config_dir + '/*', self.config_dir + '/*/*']

    def get_hosts(self):
        r = {}
        text = self.read()

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
        return r

    def save_host(self, host):
        id = host.name
        id = id.replace('*','\*')
        id = id.replace('.','\.')
    
        text = self.read()
    
        pat = re.compile('(?:#\s*)*<VirtualHost ' + id + '>(.+?)</VirtualHost>', re.S)
        res = pat.search(text)
    
        if res:
            host_text = host.config
            host_text = host_text.replace('\n', '\n#')
            host_text = '#' + host_text
            text = text.replace(res.group(0), host_text)
            self.save(text)
        else:    
            self.save(text + '\n\n' + host.config)

    def delete_host(self, id):
        id = id.replace('*','\*')
        id = id.replace('.','\.')
        text = self.read()
        text = repl_pat.sub('', text)
        self.save(text)

    def disable_host(self, id):
        id = id.replace('*','\*')
        id = id.replace('.','\.')
        text = self.read()
        pat = re.compile('(?:#\s*)*<VirtualHost ' + id + '>(.+?)</VirtualHost>', re.S)
        res = pat.search(text)
        host_text = res.group(0)
        host_text = host_text.replace('\n', '\n#')
        host_text = '#' + host_text
        text = text.replace(res.group(0), host_text)
        self.save(text)

    def enable_host(self, id):
        id = id.replace('*','\*')
        id = id.replace('.','\.')
        text = self.read()
        pat = re.compile('#\s*<VirtualHost ' + id + '>(.+?)#\s*</VirtualHost>', re.S)
        res = pat.search(text)
        host_text = res.group(0)
        host_text = host_text.replace('\n#', '\n')
        host_text = host_text[1:]
        text = text.replace(res.group(0), host_text)
        self.save(text)
          
    def get_mods(self):
        r = {}
        text = self.read()
        pat = re.compile('LoadModule\s+(.+?)\s+(.+?)\s', re.S)
        for m in pat.finditer(text):
            beg = m.start()
            while(text[beg] != '\n' and beg > 0):
                beg = beg - 1
            enabled = not (text[beg + 1] == '#')
            item = apis.webserver.Module()
            item.name = str(m.group(1))
            item.enabled = enabled
            item.has_config = True
            item.config = m.group(0)
            r[item.name] = item 
        return r
        
    def enable_mod(self, name):
        text = self.read()
        pat = re.compile('#\s*LoadModule\s+'+ name + '.+?\n', re.S)
        res = pat.search(text)
        host_text = res.group(0)
        host_text = host_text.replace('\n#', '\n')
        host_text = host_text[1:]
        text = text.replace(res.group(0), host_text)
        self.save(text)

    def disable_mod(self, name):
        text = self.read()
        pat = re.compile('(?:#\s*)*LoadModule\s+' + name + '.+?\n', re.S)
        res = pat.search(text)
        host_text = res.group(0)
        host_text = '#' + host_text
        text = text.replace(res.group(0), host_text)
        self.save(text)
    
    def save_mod(self, mod):
        text = self.read()
        pat = re.compile('LoadModule\s+' + mod.name + '.+?\n', re.S);
        res = pat.search(text)
        text = text.replace(res.group(0), mod.config)
        self.save(text)
        
    def read(self):
        return ConfManager.get().load('apache', self.config_path)
    
    def save(self, t):
        ConfManager.get().save('apache', self.config_path, t)
        ConfManager.get().commit('apache')
        
        
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
    platform = ['centos']
    text = 'Apache 2'
    icon = '/dl/apache/icon.png'
    folder = 'servers'
    ws_service = 'apache2'
    ws_name = 'apache'
    ws_icon = '/dl/apache/icon.png'
    ws_title = 'Apache 2'
    ws_backend = ApacheSingleConfigBackend
    ws_mods = True
