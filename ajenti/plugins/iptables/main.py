from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import IPTablesConfig
from reconfigure.items.iptables import TableData, ChainData, RuleData, OptionData, ArgumentData


@plugin
class Firewall (SectionPlugin):
    def init(self):
        self.title = 'Firewall'
        self.category = 'System'

        self.append(self.ui.inflate('iptables:main'))

        self.config = IPTablesConfig(path='/etc/iptables.up.rules')
        self.binder = Binder(None, self.find('config'))
        self.find('tables').new_item = lambda c: TableData()
        self.find('chains').new_item = lambda c: ChainData()
        self.find('rules').new_item = lambda c: RuleData()
        self.find('options').new_item = lambda c: OptionData()

    def on_page_load(self):
        self.config.load()
        self.binder.reset(self.config.tree).autodiscover().populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
