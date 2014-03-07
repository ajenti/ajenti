from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.util import platform_select

from reconfigure.configs import SquidConfig
from reconfigure.items.squid import ACLData, HTTPAccessData, HTTPPortData, HTTPSPortData, ArgumentData


@plugin
class Squid (SectionPlugin):
    def init(self):
        self.title = 'Squid'
        self.icon = 'exchange'
        self.category = _('Software')
        self.append(self.ui.inflate('squid:main'))

        self.find('servicebar').name = platform_select(
            debian='squid3',
            centos='squid',
            default='squid',
        )
        self.find('servicebar').reload()

        self.binder = Binder(None, self.find('config'))
        self.find('acl').new_item = lambda c: ACLData(name='new')
        self.find('http_access').new_item = lambda c: HTTPAccessData()
        self.find('http_port').new_item = lambda c: HTTPPortData()
        self.find('https_port').new_item = lambda c: HTTPSPortData()
        for e in self.nearest(lambda x: x.id == 'options'):
            e.new_item = lambda c: ArgumentData()
        self.config = SquidConfig(path='/etc/squid3/squid.conf')

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self.binder.setup(self.config.tree).populate()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        self.config.save()
        self.refresh()
