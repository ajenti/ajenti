from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on

from reconfigure.configs import SambaConfig
from reconfigure.items.samba import ShareData


@plugin
class Samba (SectionPlugin):
    def init(self):
        self.title = 'Samba'
        self.icon = 'folder-close'
        self.category = 'Software'
        self.append(self.ui.inflate('samba:main'))

        self.binder = Binder(None, self.find('config'))
        self.find('shares').new_item = lambda c: ShareData()
        self.config = SambaConfig(path='/etc/samba/smb.conf')

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        #self.mgr.fill(self.config.tree.programs)
        self.binder.reset(self.config.tree).autodiscover().populate()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        self.config.save()
        self.refresh()
