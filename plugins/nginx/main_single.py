from ajenti.api import *
from ajenti.com import *
from ajenti.utils import *
from ajenti import apis

import os
import re
import glob
import sys

class NginxSingleConfigBackend(Plugin):
    implements(IConfigurable)
    platform = ['freebsd', 'nginx', 'arch']
    config_file = ''
    name = 'nginx'
    id = 'nginx'
    
    
    def __init__(self):
        self.config_file = self.app.get_config(self).cfg_file
        if not os.path.exists(self.config_file):
            raise ConfigurationError('Can\'t find config file')
    
    def list_files(self):
        return [self.config_file]
    
    def read(self):
        return ConfManager.get().load('nginx', self.config_file)
    
    def save(self, t):
        ConfManager.get().save('nginx', self.config_file, t)
        ConfManager.get().commit('nginx')
    
    def get_hosts(self):
        res = {}
        text = self.read()
        pat = re.compile('server\s*\{\s*', re.S)
        last = 0
        for m in pat.finditer(text):
            item = apis.webserver.VirtualHost()
            t = m.start()
            if t <= last:
               continue
            while(text[t] != '\n' and t > 0 and text[t] != '#'):
               t = t - 1         
            enabled = text[t] != '#'
            item.start = t
            beg = m.start()
            open = 1;  
            if enabled:
                pat_brack = re.compile('[\{\}]', re.S)
                for bracket in pat_brack.finditer(text, m.end() + 1):
                    if bracket.group() == '{':
                        open = open + 1
                    else:
                        open = open - 1
                    last = bracket.start()
                    if open == 0:
                        break
                if open != 0:
                    continue
                item.end = last + 2
                item.config = text[beg:last + 1]
            else:
                pat_brack = re.compile('\s*#([\{\}])', re.S)
                _last = 0;
                for bracket in pat_brack.finditer(text, m.end() + 1):
                    print bracket.group(1)
                    if bracket.group(1) == '{':
                        open = open + 1
                    else:
                        open = open - 1
                    _last = bracket.end()
                    if open == 0: 
                        break
                if open != 0:
                    continue;
                config = text[m.end():_last - 1]
                lines = config.split('\n');
                bad = False
                for line in lines:
                    line = line.strip()
                    if(line != '' and line[0] != '#'):
                        bad = True
                        break
                if bad:
                    continue
                config = text[beg:_last]
                last = item.end = _last + 1
                item.config = re.sub('\ *#\s*', '', config)
            pat_name = re.compile('listen\s*(.+?);', re.S)
            name = pat_name.search(item.config)
            pat_name = re.compile('server_name\s*(.+?);', re.S)
            servername = pat_name.search(item.config)
            if(not name or not servername):
                continue
            item.name = name.group(1) + " " + servername.group(1)
            item.enabled = enabled
            res[item.name] = item
        return res

    def delete_host(self, id):
        text = self.read()
        try:
            host = self.get_hosts()[id]
        except KeyError:
            return
        text = text[:host.start] + text[host.end:]
        self.save(text)

    def save_host(self, host):
        text = self.read()
        try:
            oldhost = self.get_hosts()[host.name]
            text = text[:oldhost.start] + "\n" + host.config + text[oldhost.end:]
        except KeyError:
            text = text + "\n" + host.config
        self.save(text)
    
    def disable_host(self, id):
        text = self.read()
        try:
            host = self.get_hosts()[id]
        except KeyError:
            return
        if not host.enabled:
            return
        config = text[host.start:host.end].replace('\n', '\n#')
        text = text[:host.start] + config[:-1] + text[host.end:]
        self.save(text)
    
    def enable_host(self, id):
        text = self.read()
        try:
            host = self.get_hosts()[id]
        except KeyError:
            return
        if host.enabled:
            return
        config = text[host.start:host.end].replace('\n#', '\n')
        text = text[:host.start] + config[1:] + text[host.end:]
        self.save(text)

    host_template = """
server {
listen 80;
server_name %s;
access_log /var/log/nginx/localhost.access_log main;
error_log /var/log/nginx/localhost.error_log info;
root /var/www/localhost/htdocs;
}
"""

class NginxSCPPlugin(apis.webserver.WebserverPlugin):
    platform = ['freebsd', 'arch', 'gentoo', 'centos', 'mandriva']
    text = 'nginx'
    icon = '/dl/nginx/icon.png'
    folder = 'servers'
    ws_service = 'nginx'
    ws_name = 'nginx'
    ws_icon = '/dl/nginx/icon.png'
    ws_title = 'nginx'
    ws_backend = NginxSingleConfigBackend

