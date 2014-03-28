from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import HostsConfig
from reconfigure.items.hosts import AliasData, HostData


@plugin
class Hosts (SectionPlugin):
    def init(self):
        self.title = _('Hosts')
        self.icon = 'sitemap'
        self.category = _('System')

        self.append(self.ui.inflate('hosts:main'))

        self.config = HostsConfig(path='/etc/hosts')
        self.binder = Binder(None, self.find('hosts-config'))
        self.find('aliases').new_item = lambda c: AliasData()
        self.find('hosts').new_item = lambda c: HostData()

    def on_page_load(self):
        self.config.load()
        self.binder.setup(self.config.tree).populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
