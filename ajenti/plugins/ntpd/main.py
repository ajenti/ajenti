import re
from datetime import datetime
import os
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

open_ntpd_conf = '/etc/openntpd/ntpd.conf'
ntpd_conf = '/etc/ntp.conf'


def isopenntpd():
    return not ServiceMultiplexor.get().get_one('openntpd') is None


class NTPDData(BoundData):
    pass


class ServerData(BoundData):
    def template(self):
        return Node(
            'line',
            Node('token', PropertyNode('value', 'server')),
            Node('token', PropertyNode('value', '0.pool.ntp.org')),
        )


NTPDData.bind_collection('servers', selector=lambda x: x.children[0].get('value').value == 'server',
                         item_class=ServerData)
ServerData.bind_property('value', 'address', path=lambda x: x.children[1])


class NTPDConfig(Reconfig):
    def __init__(self, **kwargs):
        k = {
            'parser': SSVParser(),
            'builder': BoundBuilder(NTPDData),
        }
        k.update(kwargs)
        Reconfig.__init__(self, **k)


@plugin
class NTPDPlugin(SectionPlugin):
    def get_tz_debian(self):
        return open('/etc/timezone').read().strip()

    def get_tz_nondebian(self):
        return os.path.realpath('/etc/localtime')[len('/usr/share/zoneinfo/'):] if os.path.islink(
            '/etc/localtime') else ''

    def set_tz_debian(self, timezone):
        open('/etc/timezone', 'w').write(timezone + '\n')

    def set_tz_nondebian(self, timezone):
        tz = os.path.join('/usr/share/zoneinfo/', timezone)
        if os.path.exists('/etc/localtime'):
            os.unlink('/etc/localtime')
        os.symlink(tz, '/etc/localtime')

    openntpd = isopenntpd()

    service_name = platform_select(
        default='openntpd' if openntpd else 'ntp',
        centos='openntpd' if openntpd else 'ntpd',
        mageia='ntpd',
    )

    get_tz = platform_select(
        debian=get_tz_debian,
        default=get_tz_nondebian,
    )

    set_tz = platform_select(
        debian=set_tz_debian,
        default=set_tz_nondebian,
    )

    def init(self):
        self.title = _('Date & Time')
        self.icon = 'time'
        self.category = _('System')

        self.append(self.ui.inflate('ntpd:main'))

        self.find('servicebar').name = self.service_name
        self.find('servicebar').reload()

        self.config = NTPDConfig(path=platform_select(
            default=open_ntpd_conf if self.openntpd else ntpd_conf,
            centos='/usr/local/etc/ntpd.conf' if self.openntpd else ntpd_conf,
            freebsd='/usr/local/etc/ntpd.conf' if self.openntpd else ntpd_conf,
        ))

        self.binder = Binder(None, self)

        self.available_zones = []
        for d, dirs, files in os.walk('/usr/share/zoneinfo', followlinks=False):
            for f in files:
                if f != 'zone.tab':
                    self.available_zones.append(os.path.join(d, f))
        self.available_zones = [x[len('/usr/share/zoneinfo/'):] for x in self.available_zones]
        self.available_zones.sort()

        self.find('servers').new_item = lambda c: ServerData()

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self.now = int(time.time())
        self.timezone = self.get_tz()
        self.binder.setup(self).populate()

    @on('set', 'click')
    def on_set(self):
        self.binder.update()
        d = datetime.fromtimestamp(self.now)
        s = d.strftime('%m%d%H%M%Y')
        self.set_tz(self.timezone)
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
