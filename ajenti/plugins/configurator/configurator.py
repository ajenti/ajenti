import os
import re

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin


@plugin
class Configurator (SectionPlugin): 
    def init(self):
        self.title = 'Configure'

        self.append(self.ui.inflate('configurator:main'))
    