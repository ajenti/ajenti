from datetime import datetime
import time
import subprocess

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.plugins.services.api import ServiceMultiplexor
from ajenti.ui import on
from ajenti.ui.binder import Binder
from ajenti.util import platform_select

from reconfigure.configs.base import Reconfig
from reconfigure.parsers import SSVParser
from reconfigure.builders import BoundBuilder
from reconfigure.nodes import Node, PropertyNode
from reconfigure.items.bound import BoundData


class NTPDData (BoundData):
    pass


class ServerData (BoundData):
    def template(self):
        return Node(
            'line',
            Node('token', PropertyNode('value',  'server')),
            Node('token', PropertyNode('value', '0.pool.ntp.org')),
        )


NTPDData.bind_collection('servers', selector=lambda x: x.children[0].get('value').value == 'server', item_class=ServerData)
ServerData.bind_property('value', 'address', path=lambda x: x.children[1])


class NTPDConfig (Reconfig):
    def __init__(self, **kwargs):
        k = {
            'parser': SSVParser(),
            'builder': BoundBuilder(NTPDData),
        }
        k.update(kwargs)
        Reconfig.__init__(self, **k)


@plugin
class NTPDPlugin (SectionPlugin):
    service_name = platform_select(
        default='ntp',
        centos='ntpd',
    )

    def init(self):
        self.title = _('Date & Time')
        self.icon = 'time'
        self.category = _('Software')

        self.append(self.ui.inflate('ntpd:main'))

        self.find('servicebar').name = self.service_name
        self.find('servicebar').reload()

        self.config = NTPDConfig(path=platform_select(
            default='/etc/ntp.conf',
        ))

        self.binder = Binder(None, self)

        self.find('servers').new_item = lambda c: ServerData()

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self.now = int(time.time())
        self.binder.setup(self).populate()

    @on('set', 'click')
    def on_set(self):
        self.binder.update()
        d = datetime.fromtimestamp(self.now)
        s = d.strftime('%m%d%H%M%Y') 
        subprocess.call(['date', s])
        self.refresh()

    @on('sync', 'click')
    def on_sync(self):
        self.binder.update()
        if len(self.config.tree.servers) == 0:
            self.context.notify('error', _('No servers defined'))
            return
        server = self.config.tree.servers[0].address
        output = subprocess.check_output(['ntpdate', '-u', server])
        self.context.notify('info', _('Done'))
        self.context.notify('info', output)
        self.refresh()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
        self.refresh()
        self.context.notify('info', _('Saved'))
        ServiceMultiplexor.get().get_one(self.service_name).restart()
