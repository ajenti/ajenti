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


class Sink1Data (BoundData):
    def template(self):
        return Node(
            'line',
            Node('token', PropertyNode('value', 'trapsink')),
            Node('token', PropertyNode('value', 'localhost public')),
        )


class Sink2Data (BoundData):
    def template(self):
        return Node(
            'line',
            Node('token', PropertyNode('value', 'trap2sink')),
            Node('token', PropertyNode('value', 'localhost public')),
        )


class Sink2cData (BoundData):
    def template(self):
        return Node(
            'line',
            Node('token', PropertyNode('value', 'informsink')),
            Node('token', PropertyNode('value', 'localhost public')),
        )

SNMPDData.bind_collection('rocommunities', selector=lambda x: x.children[0].get('value').value == 'rocommunity', item_class=ROCommunityData)
SNMPDData.bind_collection('rwcommunities', selector=lambda x: x.children[0].get('value').value == 'rwcommunity', item_class=RWCommunityData)
SNMPDData.bind_collection('sinks1', selector=lambda x: x.children[0].get('value').value == 'trapsink', item_class=Sink1Data)
SNMPDData.bind_collection('sinks2', selector=lambda x: x.children[0].get('value').value == 'trap2sink', item_class=Sink2Data)
SNMPDData.bind_collection('sinks2c', selector=lambda x: x.children[0].get('value').value == 'informsink', item_class=Sink2cData)
ROCommunityData.bind_property('value', 'value', path=lambda x: x.children[1])
RWCommunityData.bind_property('value', 'value', path=lambda x: x.children[1])
for s in [Sink1Data, Sink2Data, Sink2cData]:
    s.bind_property('value', 'value', path=lambda x: x.children[1])


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
        self.find('sinks1').new_item = lambda c: Sink1Data()
        self.find('sinks2').new_item = lambda c: Sink2Data()
        self.find('sinks2c').new_item = lambda c: Sink2cData()

        self.binder = Binder(None, self)

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.snmp_config.load()
        self.snmpd_config.load()

        self.rocommunities = self.snmpd_config.tree.rocommunities
        self.rwcommunities = self.snmpd_config.tree.rwcommunities
        self.sinks1 = self.snmpd_config.tree.sinks1
        self.sinks2 = self.snmpd_config.tree.sinks2
        self.sinks2c = self.snmpd_config.tree.sinks2c

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
