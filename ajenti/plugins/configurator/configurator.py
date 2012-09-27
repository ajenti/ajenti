import os
import re

import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder, CollectionBindInfo


@plugin
class Configurator (SectionPlugin): 
    def init(self):
        self.title = 'Configure'

        self.append(self.ui.inflate('configurator:main'))

        self.binder = Binder(ajenti.config.tree, self.find('ajenti-config'))
        ajenti.config.tree.users__bind = CollectionBindInfo(
            template = lambda x: self.ui.inflate('configurator:user'),
            values = lambda x: x.values(),
        )
        self.binder.autodiscover()
        self.binder.populate()

        self.find('save-button').on('click', self.save)

    def save(self):
    	self.binder.update()
    	ajenti.config.save()
    