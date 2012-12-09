from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import ResolvConfig
from reconfigure.items.resolv import ItemData


@plugin
class Resolv (SectionPlugin):
    def init(self):
        self.title = 'Nameservers'
        self.category = 'System'

        self.append(self.ui.inflate('resolv:main'))
        self.find('name-box').labels = ['DNS nameserver', 'Local domain name', 'Search list', 'Sort list', 'Options']
        self.find('name-box').values = ['nameserver', 'domain', 'search', 'sortlist', 'options']

        self.config = ResolvConfig(path='/etc/resolv.conf')
        self.binder = Binder(None, self.find('resolv-config'))
        self.find('items').new_item = lambda c: ItemData()

    def on_page_load(self):
        self.config.load()
        self.binder.reset(self.config.tree).autodiscover().populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
