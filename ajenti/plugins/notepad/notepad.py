import os
import re

import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder
from ajenti.users import UserManager

from reconfigure.ext.nginx import NginxConfig


@plugin
class Notepad (SectionPlugin): 
    def init(self):
        self.title = 'Notepad'
        self.append(self.ui.inflate('notepad:main'))
        self.opendialog = self.find('opendialog')
