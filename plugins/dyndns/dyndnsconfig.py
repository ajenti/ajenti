import os

from ajenti.api import *
from ajenti.utils import *
from ajenti.com import *

class DynDnsProperty:
    def __init__(self):
        self.field = '';
        self.value = '';

class Config (Plugin):
    implements(IConfigurable)
    name = 'Dyndns Configuration'
    id = 'inadyn'
    pathfile = '/etc/inadyn.conf'

    def list_files(self):
        return [self.pathfile]

    def read(self):
        if not os.path.isfile(self.pathfile):
            f = open(self.pathfile,'w')
            f.close()
            return

        file = ConfManager.get().load('inadyn', self.pathfile).split('\n')
        c = []

        if file is not None:
            for f in file:
                if f != '' :
                    try:
                        s = f.split('\t')
                        field, val = s
                        d = DynDnsProperty()
                        d.field = field
                        d.value = val
                        c.append(d)
                    except:
                        pass
        return c

    def save(self, data):
        if not os.path.isfile(self.pathfile):
            f = open(self.pathfile,'w')
            f.close()
            
        data_row = ''
        for a_data in data:
            data_row += '%s\t%s\n' % (a_data.field, a_data.value)
        ConfManager.get().save('inadyn', self.pathfile, data_row)
        ConfManager.get().commit('inadyn')
