import os
import re

import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder


@plugin
class Configurator (SectionPlugin): 
    def init(self):
        self.title = 'Configure'

        self.append(self.ui.inflate('configurator:main'))

        self.binder = Binder(ajenti.config.tree, self.find('ajenti-config'))
        self.binder.autodiscover()
        self.binder.populate()
    