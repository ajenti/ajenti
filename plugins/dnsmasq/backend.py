from ajenti.com import *
import re

class Backend(Plugin):

    def __init__(self):
        self.lease_file = '/var/lib/misc/dnsmasq.leases'
        self.config_file = '/etc/dnsmasq.conf'

    def get_leases(self):
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
            'opts': {}
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
                    elif k == 'domain':
                        r['domains'].append(v)
                    else:
                        r['opts'][k] = v
                else:
                    k = l.strip()
                    r['opts'][k] = None
        return r                    
        
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
                r.append('apply option set %s' % x[1])
            if x[0] == 'ignore':
                r.append('ignore')
            if x[0] == 'name':
                r.append('set name %s' % x[1])
            if x[0] == 'time':
                r.append('%s lease' % x[1])
        return ', '.join(r)
                      
