import os
import re
import mimetypes

import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder
from ajenti.users import UserManager

from reconfigure.configs import HostsConfig
from reconfigure.items.hosts import Alias, Host


@plugin
class Hosts (SectionPlugin): 
    def init(self):
        self.title = 'Hosts'
        self.append(self.ui.inflate('hosts:main'))

        self.config = HostsConfig(path='/etc/hosts')
        self.config.load()
        self.binder = Binder(self.config.tree, self.find('hosts-config'))
        self.find('aliases').new_item = lambda c: Alias()
        self.find('hosts').new_item = lambda c: Host()
        self.binder.autodiscover()
        self.binder.populate()

        self.find('save').on('click', self.save)

    def save(self):
        self.binder.update()
        self.config.save() 
        self.publish()