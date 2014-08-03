from ajenti.api import *
from ajenti.api.sensors import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import *
from ajenti.ui.binder import Binder

from api import *


@plugin
class NetworkPlugin (SectionPlugin):
    platforms = ['debian', 'centos', 'mageia']

    def init(self):
        self.title = _('Network')
        self.icon = 'globe'
        self.category = _('System')
        self.net_config = INetworkConfig.get()

        self.append(self.ui.inflate('network:main'))

        def post_interface_bind(o, c, i, u):
            i.add_bits(self.ui)
            for bit in i.bits:
                u.find('bits').append(self.ui.create(
                    'tab',
                    children=[bit],
                    title=bit.title,
                ))
            u.find('up').on('click', self.on_up, i)
            u.find('down').on('click', self.on_down, i)
            u.find('restart').on('click', self.on_restart, i)
            u.find('ip').text = self.net_config.get_ip(i)

        def post_interface_update(o, c, i, u):
            for bit in i.bits:
                bit.apply()

        self.find('interfaces').post_item_bind = post_interface_bind
        self.find('interfaces').post_item_update = post_interface_update

        self.binder = Binder(None, self)

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.net_config.rescan()

        sensor = Sensor.find('traffic')
        for i in self.net_config.interface_list:
            i.tx, i.rx = sensor.value(i.name)

        self.binder.setup(self.net_config).populate()
        return

    def on_up(self, iface=None):
        self.save()
        self.net_config.up(iface)
        self.refresh()

    def on_down(self, iface=None):
        self.save()
        self.net_config.down(iface)
        self.refresh()

    def on_restart(self, iface=None):
        self.save()
        self.on_down(iface)
        self.on_up(iface)

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.net_config.save()
        self.refresh()
        self.context.notify('info', _('Saved'))
