from ajenti.api import *
from ajenti.com import *


class ServiceGroups (Plugin):
    def __init__(self):
        self.read()

    def read(self):
        if not self.app.config.has_section('services'):
            self.app.config.add_section('services')

        r = {}
        names = {}
        content = {}
        for n in self.app.config.options('services'):
            if n.startswith('groupname-'):
                names[n.split('-')[1]] = self.app.config.get('services', n)
            if n.startswith('groupcontent-'):
                content[n.split('-')[1]] = self.app.config.get('services', n)

        for n in names.keys():
            r[names[n]] = content[n].split(' ')

        self.groups = r

    def save(self):
        if self.app.config.has_section('services'):
            self.app.config.remove_section('services')
        self.app.config.add_section('services')

        idx = 0
        for i in self.groups.keys():
            self.app.config.set('services', 'groupname-%i'%idx, i)
            self.app.config.set('services', 'groupcontent-%i'%idx, ' '.join(self.groups[i]))
            idx += 1
            
        self.app.config.save()