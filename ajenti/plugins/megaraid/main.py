from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import ResolvConfig
from reconfigure.items.resolv import ItemData

from api import RAIDManager


@plugin
class RAID (SectionPlugin):
    def init(self):
        self.title = 'LSI MegaRAID'
        self.icon = 'hdd'
        self.category = _('System')

        self.append(self.ui.inflate('megaraid:main'))

        self.mgr = RAIDManager.get()
        self.binder = Binder(None, self)

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.mgr.refresh()
        self.binder.setup(self.mgr).populate()
