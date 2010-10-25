import os

from ajenti.utils import *
from ajenti.plugins.uzuri_common import ClusteredConfig


class SquidConfig(ClusteredConfig):
    name = 'Squid'
    id = 'squid'
    files = [('/etc/squid', '*')] 
    run_after = ['service squid restart']

    misc = []
    acls = []
    rules = []
    http_port = []
    https_port = []
    ref_pats = []

    access_lists = [
        'http_access',
        'http_reply_access',
        'icp_access',
        'miss_access',
        'cache',
        'url_rewrite_access',
        'ident_lookup_access',
        'always_direct',
        'never_direct',
        'snmp_access',
        'broken_posts',
        'cache_peer_access',
        'htcp_access',
        'htcp_clr_access',
        'request_header_access',
        'reply_header_access',
        'delay_access',
        'icap_access',
        'adaptation_access',
        'log_access'
       ]

    def __init__(self):
        self.cfg_file = self.app.get_config(self).cfg_file
        
    def load(self):
        self.misc = []
        self.acls = []
        self.rules = []
        self.http_port = []
        self.https_port = []
        self.ref_pats = []

        ss = self.open(self.cfg_file).read().split('\n')

        for s in ss:
            if len(s) > 0 and s[0] != '#':
                try:
                    s = s.split(' ')
                    k = s[0]
                    v = ' '.join(s[1:])
                    if k == 'acl':
                        v = v.split(' ')
                        an = v[0]
                        at = v[1]
                        av = ' '.join(v[2:])
                        self.acls.append((an, at, av))
                    elif k in self.access_lists:
                        v = v.split(' ')
                        al = k
                        an = v[0]
                        av = ' '.join(v[1:])
                        self.rules.append((al, an, av))
                    elif k == 'http_port':
                        v = v.split(':')
                        self.http_port.append((v[0], v[1]))
                    elif k == 'https_port':
                        v = v.split(':')
                        self.https_port.append((v[0], v[1]))
                    elif k == 'refresh_pattern':
                        v = v.split()
                        o = ''
                        if v[0] == '-i':
                            v.remove('-i')
                            o = '-i '
                        if len(v) > 4:
                            o += ' '.join(v[4:])
                        self.ref_pats.append((v[0], v[1], v[2], v[3], o))
                    else:
                        self.misc.append((k, v))
                except:
                    pass

    def save(self):
        s = ''

        s += '\n# Bindings\n'
        for k,v in self.http_port:
            s += 'http_port %s:%s\n' % (k,v)
        for k,v in self.https_port:
            s += 'https_port %s:%s\n' % (k,v)

        s += '\n# ACLs\n'
        for k,t,v in self.acls:
            s += 'acl %s %s %s\n' % (k,t,v)

        s += '\n# Access rules\n'
        for t,k,v in self.rules:
            s += '%s %s %s\n' % (t,k,v)

        s += '\n# Refresh patterns\n'
        for r,mn,p,mx,o in self.ref_pats:
            s += 'refresh_pattern ';
            if '-i' in o.split():
                s += '-i '
                o = o[2:]
            s += '%s %s %s %s %s\n' % (r,mn,p,mx,o)

        s += '\n# Misc options\n'
        for k,v in self.misc:
            s += '%s %s\n' % (k,v)

        with self.open(self.cfg_file, 'w') as f:
            f.write(s)
