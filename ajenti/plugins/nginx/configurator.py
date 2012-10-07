import os
import re

import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder
from ajenti.users import UserManager

from reconfigure.configs import NginxConfig


@plugin
class Configurator (SectionPlugin): 
    def init(self):
        self.title = 'nginx'
        self.append(self.ui.inflate('nginx:main'))

        self.config = NginxConfig(path='/etc/nginx/nginx.conf')
        self.config.load()
        
        self.binder = Binder(self.config.tree, self.find('nginx-config'))
        #self.config.tree.http.servers__bind = CollectionBindInfo(
            #template = lambda x: self.ui.inflate('nginx:server'),
            #values = lambda x: x.values(),
            #new_item = lambda: User('Unnamed', ''),
            #add_item = lambda x: ajenti.config.tree.users.update({x.name: x}),
            #delete_item = lambda x: ajenti.config.tree.users.pop(x.name),
        #)
        self.binder.autodiscover()
        self.binder.populate()

        self.find('save').on('click', self.save)

    def save(self):
    	self.binder.update()
        self.config.save() 
        self.publish()
    