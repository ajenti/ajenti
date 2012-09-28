import os
import re

import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder, CollectionBindInfo
from ajenti.users import UserManager
from reconfigure.ext.ajenti.items import User


@plugin
class Configurator (SectionPlugin): 
    def init(self):
        self.title = 'Configure'

        self.append(self.ui.inflate('configurator:main'))

        self.binder = Binder(ajenti.config.tree, self.find('ajenti-config'))
        ajenti.config.tree.users__bind = CollectionBindInfo(
            template = lambda x: self.ui.inflate('configurator:user'),
            values = lambda x: x.values(),
            new_item = lambda: User('Unnamed', ''),
            add_item = lambda x: ajenti.config.tree.users.update({x.name: x}),
            delete_item = lambda x: ajenti.config.tree.users.pop(x.name),
        )
        self.binder.autodiscover()
        self.binder.populate()

        self.find('save-button').on('click', self.save)

    def save(self):
    	self.binder.update()
        for user in ajenti.config.tree.users.values():
            user.password = UserManager.get().hash_password(user.password)
        self.binder.populate()
        ajenti.config.save()
        self.publish()
    