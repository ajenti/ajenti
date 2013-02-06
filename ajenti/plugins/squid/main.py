from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on

from reconfigure.configs import SquidConfig
from reconfigure.items.squid import ACLData


@plugin
class Squid (SectionPlugin):
    def init(self):
        self.title = 'Squid'
        self.icon = 'exchange'
        self.category = 'Software'
        self.append(self.ui.inflate('squid:main'))

        self.binder = Binder(None, self.find('config'))
        self.find('acl').new_item = lambda c: ACLData()
        self.config = SquidConfig(path='/etc/squid3/squid.conf')

        #def post_item_bind(object, collection, item, ui):
        #   ui.find('disconnect').on('click', self.on_disconnect, item)
        #self.find('connections').post_item_bind = post_item_bind

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self.binder.reset(self.config.tree).autodiscover().populate()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        self.config.save()
        self.refresh()
