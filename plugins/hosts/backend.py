import re
import os

from ajenti.utils import *

class Host:
    def __init__(self):
        self.ip = '';
        self.name = '';
        self.aliases = '';

def read():
    ss = open('/etc/hosts', 'r').read().split('\n')
    r = []

    for s in ss:
        if s != '' and s[0] != '#':
            try:
                s = s.split()
                h = Host()
                try:
                    h.ip = s[0]
                    h.name = s[1]
                    for i in range(2, len(s)):
                        h.aliases += '%s ' % s[i]
                    h.aliases = h.aliases.rstrip();
                except:
                    pass
                r.append(h)
            except:
                pass

    return r

def save(hh):
    d = ''
    for h in hh:
        d += '%s\t%s\t%s\n' % (h.ip, h.name, h.aliases)
    with open('/etc/hosts', 'w') as f:
        f.write(d)
