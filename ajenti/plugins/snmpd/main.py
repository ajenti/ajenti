import os
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


# SNMP

class SNMPData (BoundData):
    pass


class MIBData (BoundData):
    def template(self):
        return Node(
            'line',
            Node('token', PropertyNode('value', 'mibs')),
            Node('token', PropertyNode('value', 'IF-MIB')),
        )


SNMPData.bind_collection('mibs', selector=lambda x: x.children[0].get('value').value == 'mibs', item_class=MIBData)
MIBData.bind_property('value', 'name', path=lambda x: x.children[1])


class SNMPConfig (Reconfig):
    def __init__(self, **kwargs):
        k = {
            'parser': SSVParser(),
            'builder': BoundBuilder(SNMPData),
        }
        k.update(kwargs)
        Reconfig.__init__(self, **k)


# SNMPD 

class SNMPDData (BoundData):
    pass


class ROCommunityData (BoundData):
    def template(self):
        return Node(
            'line',
            Node('token', PropertyNode('value', 'rocommunity')),
            Node('token', PropertyNode('value', 'public 192.168.0.0/24')),
        )


class RWCommunityData (BoundData):
    def template(self):
        return Node(
            'line',
            Node('token', PropertyNode('value', 'rwcommunity')),
            Node('token', PropertyNode('value', 'public 192.168.0.0/24')),
        )


SNMPDData.bind_collection('rocommunities', selector=lambda x: x.children[0].get('value').value == 'rocommunity', item_class=ROCommunityData)
SNMPDData.bind_collection('rwcommunities', selector=lambda x: x.children[0].get('value').value == 'rwcommunity', item_class=RWCommunityData)
ROCommunityData.bind_property('value', 'value', path=lambda x: x.children[1])
RWCommunityData.bind_property('value', 'value', path=lambda x: x.children[1])


class SNMPDConfig (Reconfig):
    def __init__(self, **kwargs):
        k = {
            'parser': SSVParser(maxsplit=1),
            'builder': BoundBuilder(SNMPDData),
        }
        k.update(kwargs)
        Reconfig.__init__(self, **k)



@plugin
class SNMPDPlugin (SectionPlugin):
    service_name = platform_select(
        default='snmpd',
    )

    def init(self):
        self.title = 'SNMP'
        self.icon = 'exchange'
        self.category = _('Software')

        self.append(self.ui.inflate('snmpd:main'))

        self.find('servicebar').name = self.service_name
        self.find('servicebar').reload()

        self.snmp_config = SNMPConfig(path=platform_select(
            default='/etc/snmp/snmp.conf',
        ))
        self.snmpd_config = SNMPDConfig(path=platform_select(
            default='/etc/snmp/snmpd.conf',
        ))

        self.find('rocommunities').new_item = lambda c: ROCommunityData()
        self.find('rwcommunities').new_item = lambda c: RWCommunityData()

        self.binder = Binder(None, self)

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.snmp_config.load()
        self.snmpd_config.load()

        self.rocommunities = self.snmpd_config.tree.rocommunities
        self.rwcommunities = self.snmpd_config.tree.rwcommunities

        enabled_mibs = []
        for mib in self.snmp_config.tree.mibs:
            for x in mib.name.strip('-+:').split(':'):
                enabled_mibs.append(x)
        self.mibs = []
        for dirpath, dirname, filenames in os.walk('/usr/share/mibs', followlinks=True):
            for x in filenames:
                if not x.startswith('.'):
                    mib = MIBData()
                    mib.name = x
                    mib.selected = x in enabled_mibs
                    self.mibs.append(mib)
        self.mibs = sorted(self.mibs, key=lambda x: x.name)
        self.binder.setup(self).populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        
        mib = MIBData()
        mib.name = ':'.join([x.name for x in self.mibs if x.selected])
        for x in list(self.snmp_config.tree.mibs):
            self.snmp_config.tree.mibs.remove(x)
        self.snmp_config.tree.mibs.append(mib)

        self.snmp_config.save()
        self.snmpd_config.save()

        self.refresh()
        self.context.notify('info', _('Saved'))
        ServiceMultiplexor.get().get_one(self.service_name).restart()
