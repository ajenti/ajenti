from ajenti.api import *
from ajenti.com import *
import re
import os


class Backend(Plugin):
    implements (IConfigurable)
    name = 'dnsmasq'
    id = 'dnsmasq'
    
    def __init__(self):
        self.lease_file = '/var/lib/misc/dnsmasq.leases'
        self.config_file = '/etc/dnsmasq.conf'

    def list_files(self):
        return [self.config_file]
        
    def get_leases(self):
        if not os.path.exists(self.lease_file):
            return []
            
        r = []
        for l in open(self.lease_file, 'r'):
            l = l.split(' ')
            x = {
                'mac': l[1],
                'ip': l[2],
                'host': l[3],
            }
            r.append(x)
        return r


    def get_config(self):   
        r = {
            'dhcp-hosts': [],
            'domains': [],
            'opts': {},
        }
        for l in open(self.config_file, 'r'):
            l = l.strip()
            if len(l) > 0 and not l.startswith('#'):
                if '=' in l:
                    k,v = l.split('=', 1)
                    k = k.strip()
                    v = v.strip()
                    
                    if k == 'dhcp-host':
                        r['dhcp-hosts'].append(self.parse_host(v))
                    elif k == 'address':
                        r['domains'].append(v.split('/')[1:])
                    else:
                        r['opts'][k] = v
                else:
                    k = l.strip()
                    r['opts'][k] = None
        return r                    
        
    def save_config(self, cfg):
        s = ''
        s += '# Hosts\n' 
        for x in cfg['dhcp-hosts']:
            v = []
            for y in x['id']:
                if y[0] == 'dhcpid':
                    v.append('id:'+y[1])
                else:
                    v.append(y[1])
            for y in x['act']:
                if y[0] == 'ignore':
                    v.append(y[0])
                elif y[0] == 'set':
                    v.append('set:' + y[1])
                else:
                    v.append(y[1])
            s += 'dhcp-host=' + ','.join(v) + '\n'
        
        s += '\n\n# Domains\n' 
        for x in cfg['domains']:
            s += 'address=/' + '/'.join(x) + '\n'
         
        s += '\n\n# Other options\n'
        for x in cfg['opts']:
            if cfg['opts'][x]:
                s += '%s=%s\n' % (x, cfg['opts'][x])
            else:
                s += x + '\n'
        
        open(self.config_file, 'w').write(s)
        
    def parse_host(self, s):
        r = { 'id': [], 'act': [] }
        s = s.split(',')
        for x in s:
            if re.match('([\w\*]{1,2}:){5}[\w\*]{1,2}', x): # MAC
                r['id'].append(('mac', x))
            elif re.match('id:*', x):
                r['id'].append(('dhcpid', x[3:]))
            elif re.match('(\d{1,3}\.){3}\d{1,3}', x): # IP
                r['act'].append(('ip', x))
            elif re.match('set:*', x):
                r['act'].append(('set', x[4:]))
            elif re.match('ignore', x):
                r['act'].append(('ignore', None))
            elif re.match('infinite', x):
                r['act'].append(('time', x))
            elif re.match('\d+[hmsd]', x):
                r['act'].append(('time', x))
            else:
                if r['id'] == []:
                    r['id'].append(('name', x))
                else:
                    r['act'].append(('name', x))
        return r
        
    def find_mac(self, h):
        for x in h['id']:
            if x[0] == 'mac':
                return x[1]
        return ''
        
    def find_ip(self, h):
        for x in h['act']:
            if x[0] == 'ip':
                return x[1]
        return ''
               
    def str_ident(self, h):
        r = []
        for x in h:
            if x[0] == 'dhcpid':
                r.append('client id is %s' % x[1])
            if x[0] == 'name':
                r.append('name is %s' % x[1])
        return ', '.join(r)
                      
    def str_act(self, h):
        r = []
        for x in h:
            if x[0] == 'set':
                r.append('use tag %s' % x[1])
            if x[0] == 'ignore':
                r.append('ignore')
            if x[0] == 'name':
                r.append('set name %s' % x[1])
            if x[0] == 'time':
                r.append('%s lease' % x[1])
        return ', '.join(r)
                      
