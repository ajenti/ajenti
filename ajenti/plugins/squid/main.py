from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on

from reconfigure.configs import SquidConfig
from reconfigure.items.squid import ACLData, HTTPAccessData, HTTPPortData, HTTPSPortData


@plugin
class Squid (SectionPlugin):
    def init(self):
        self.title = _('Squid')
        self.icon = 'exchange'
        self.category = _('Software')
        self.append(self.ui.inflate('squid:main'))

        self.binder = Binder(None, self.find('config'))
        self.find('acl').new_item = lambda c: ACLData()
        self.find('http_access').new_item = lambda c: HTTPAccessData()
        self.find('http_port').new_item = lambda c: HTTPPortData()
        self.find('https_port').new_item = lambda c: HTTPSPortData()
        self.config = SquidConfig(path='/etc/squid3/squid.conf')

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
