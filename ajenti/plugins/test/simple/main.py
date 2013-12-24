from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin


@plugin
class SimpleDemo (SectionPlugin):
    def init(self):
        self.title = 'Simple'
        self.icon = 'question'
        self.category = 'Demo'

        self.append(self.ui.inflate('test:simple-main'))
