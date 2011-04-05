from ajenti.com import *


class Backend(Plugin):

    def __init__(self):
        self.lease_file = '/var/lib/misc/dnsmasq.leases'

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
            

