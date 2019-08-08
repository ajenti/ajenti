import subprocess

import aj
import yaml
import os
from os.path import isfile, join
from jadi import component
from aj.plugins.network.api import NetworkManager

from .ip import ifconfig_up, ifconfig_down, ifconfig_get_ip, ifconfig_get_up

@component(NetworkManager)
class UbuntuNetworkManager(NetworkManager):
    """Use of Netplan for Ubuntu version above 18.04"""
    path = '/etc/netplan'

    @classmethod
    def __verify__(cls):
        if b'Ubuntu' in aj.platform_string:
            ubuntu_version = int(aj.platform_string[7:9])
        return aj.platform in ['debian'] and ubuntu_version >= 18

    def __init__(self, context):
        NetworkManager.__init__(self, context)

    def get_config(self):
        ifaces = []
        netplan_files = [join(self.path,f) for f in os.listdir(self.path) if isfile(join(self.path, f))]
        for path in netplan_files:
            config = yaml.load(open(path), Loader=yaml.Loader)['network']['ethernets']
            for key in config:
                iface = {
                    'name': key,
                    'family': None,
                    'addressing': None,
                    'address': config[key]['addresses'][0],
                    'mask': config[key]['addresses'][0].split('/')[1],
                    'gateway': config[key]['gateway4'],
                    'hwaddress': None,
                    'mtu': None,
                    'scope': None,
                    'metric': None,
                    'client': None,
                    'pre_up_script': None,
                    'pre_down_script': None,
                    'up_script': None,
                    'down_script': None,
                    'post_up_script': None,
                    'post_down_script': None,
                }
                ifaces.append(iface)
        ## TODO : lo is not necessarily visible in an yaml config file
        return ifaces

    def set_config(self, config):
        raise NotImplementedError ## TODO

    def get_state(self, iface):
        return {
            'address': ifconfig_get_ip(iface),
            'up': ifconfig_get_up(iface),
        }

    def up(self, iface):
        ifconfig_up(iface)

    def down(self, iface):
        ifconfig_down(iface)

    def get_hostname(self):
        return subprocess.check_output('hostname', encoding='utf-8')

    def set_hostname(self, value):
        with open('/etc/hostname', 'w') as f:
            f.write(value)
        subprocess.check_call(['hostname', value])
