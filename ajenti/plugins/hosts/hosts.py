from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import HostsConfig
from reconfigure.items.hosts import Alias, Host


@plugin
class Hosts (SectionPlugin):
    def init(self):
        self.title = 'Hosts'
        self.category = 'System'

        self.append(self.ui.inflate('hosts:main'))

        self.config = HostsConfig(path='/etc/hosts')
        self.binder = Binder(None, self.find('hosts-config'))
        self.find('aliases').new_item = lambda c: Alias()
        self.find('hosts').new_item = lambda c: Host()

    def on_page_load(self):
        self.config.load()
        self.binder.reset(self.config.tree).autodiscover().populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
