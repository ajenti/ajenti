from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on

from reconfigure.configs import SambaConfig
from reconfigure.items.samba import ShareData

from status import SambaMonitor


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

        def post_item_bind(object, collection, item, ui):
            ui.find('disconnect').on('click', self.on_disconnect, item)

        self.find('connections').post_item_bind = post_item_bind

        self.monitor = SambaMonitor()
        self.binder_m = Binder(self.monitor, self.find('status'))

    def on_page_load(self):
        self.refresh()

    def on_disconnect(self, connection):
        connection.disconnect()
        self.refresh()

    def refresh(self):
        self.config.load()
        self.monitor.refresh()
        self.binder_m.reset(self.monitor).autodiscover().populate()
        self.binder.reset(self.config.tree).autodiscover().populate()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        self.config.save()
        self.refresh()
