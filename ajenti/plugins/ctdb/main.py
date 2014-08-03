import os
import subprocess

import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import CTDBConfig, CTDBNodesConfig, CTDBPublicAddressesConfig
from reconfigure.items.ctdb import NodeData, PublicAddressData


@plugin
class CTDB (SectionPlugin):
    nodes_file = '/etc/ctdb/nodes'
    addresses_file = '/etc/ctdb/public_addresses'

    def init(self):
        self.title = _('Samba Cluster')
        self.icon = 'folder-close'
        self.category = _('Software')

        self.append(self.ui.inflate('ctdb:main'))

        self.config_path = {
            'debian': '/etc/default/ctdb',
            'centos': '/etc/sysconfig/ctdb',
            'mageia': '/etc/sysconfig/ctdb'
        }[ajenti.platform]

        self.config = CTDBConfig(path=self.config_path)
        self.config.load()

        self.binder = Binder(None, self.find('main-config'))
        self.n_binder = Binder(None, self.find('nodes-config'))
        self.a_binder = Binder(None, self.find('addresses-config'))
        self.find('nodes').new_item = lambda c: NodeData()
        self.find('addresses').new_item = lambda c: self.new_address()

    def new_address(self):
        a = PublicAddressData()
        a.address = '192.168.0.1/24'
        return a

    def on_page_load(self):
        n_path = self.config.tree.nodes_file
        self.nodes_config = CTDBNodesConfig(path=n_path)
        if not os.path.exists(n_path):
            open(n_path, 'w').close()
        self.nodes_config.load()

        a_path = self.config.tree.public_addresses_file
        self.addresses_config = CTDBPublicAddressesConfig(path=a_path)
        if not os.path.exists(a_path):
            open(a_path, 'w').close()
        self.addresses_config.load()

        self.config.load()
        self.binder.setup(self.config.tree).populate()
        self.n_binder.setup(self.nodes_config.tree).populate()
        self.a_binder.setup(self.addresses_config.tree).populate()
        self.refresh()

    @on('refresh', 'click')
    def refresh(self):
        try:
            self.find('status').value = subprocess.check_output(['ctdb', 'status'])
            self.find('status-ip').value = subprocess.check_output(['ctdb', 'ip'])
        except:
            self.find('status').value = _('Failed to obtain CTDB status')

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.n_binder.update()
        self.a_binder.update()
        self.config.save()
        self.nodes_config.save()
        self.addresses_config.save()
        self.context.notify('info', _('Saved'))
