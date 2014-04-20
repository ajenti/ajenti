from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder
from ajenti.util import platform_select

from reconfigure.configs import DHCPDConfig
from reconfigure.items.dhcpd import SubnetData, OptionData, RangeData


@plugin
class DHCPDPlugin (SectionPlugin):
    def init(self):
        self.title = _('DHCP Server')
        self.icon = 'sitemap'
        self.category = _('Software')

        self.append(self.ui.inflate('dhcpd:main'))

        self.config = DHCPDConfig(path=platform_select(
            default='/etc/dhcp/dhcpd.conf',
            arch='/etc/dhcpd.conf',
        ))

        self.binder = Binder(None, self)

        for x in self.nearest(lambda x: x.bind == 'ranges'):
            x.new_item = lambda c: RangeData()
        for x in self.nearest(lambda x: x.bind == 'options'):
            x.new_item = lambda c: OptionData()
        self.find('subnets').new_item = lambda c: SubnetData()

    def on_page_load(self):
        self.config.load()
        self.binder.setup(self.config.tree).populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
