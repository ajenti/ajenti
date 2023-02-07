import subprocess

import aj
import yaml
import os
from os.path import isfile, join
from jadi import component
from aj.plugins.network.api import NetworkManager

from .ip import *

@component(NetworkManager)
class UbuntuNetworkManager(NetworkManager):
    """
    Use of Netplan for Ubuntu version above 18.04
    """

    path = '/etc/netplan'

    @classmethod
    def __verify__(cls):
        """
        Verify if this manager is relevant. Use netplan for Ubuntu > 18.

        :return: bool
        :rtype: bool
        """

        check_prior_ubuntu = False
        if 'Ubuntu' in aj.platform_string:
            ubuntu_version = int(aj.platform_string[7:9])
            check_prior_ubuntu = ubuntu_version >= 18
        return aj.platform in ['debian'] and check_prior_ubuntu

    def __init__(self, context):
        NetworkManager.__init__(self, context)

    def get_config(self):
        """
        Parse the content of /etc/netplan.

        :return: List of iface informations, one iface per dict
        :rtype: list of dict
        """

        ifaces = []
        netplan_files = [join(self.path,f) for f in os.listdir(self.path) if isfile(join(self.path, f))]
        for path in netplan_files:
            try:
                with open(path, 'r') as netplan_config:
                    config = yaml.load(netplan_config, Loader=yaml.SafeLoader) or {}
                    network_config = config.get('network', {})
                    ethernet_config = network_config.get('ethernets', {})
            except KeyError:
                # Maybe there are some others files in /etc/netplan
                continue
            for key in ethernet_config:
                addresses = ethernet_config[key].get('adresses', None)
                if addresses is None:
                    # DHCP
                    ip, mask = ifconfig_get_ip4_mask(key)
                    gateway = ifconfig_get_gateway(key)
                else:
                    ip, mask = ethernet_config[key]['addresses'][0].split('/')
                    gateway = ethernet_config[key].get('gateway4', None)
                iface = {
                    'name': key,
                    'family': None,
                    'addressing': None,
                    'address': ip,
                    'mask': mask,
                    'gateway': gateway,
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
        ## TODO : better handle dhcp
        return ifaces

    def set_config(self, config):
        """
        Set the new config in the config file through augeas.

        :param config: List of iface informations, one dict per iface
        :type config: list of dict
        """

        raise NotImplementedError ## TODO

    def get_state(self, iface):
        """
        Get ip and status for an iface.

        :param iface: Network interface, e.g. eth0
        :type iface: string
        :return: Ip and status
        :rtype: dict
        """

        return {
            'address': ifconfig_get_ip(iface),
            'up': ifconfig_get_up(iface),
        }

    def up(self, iface):
        """
        Bring an iface up.

        :param iface: Network interface, e.g. eth0
        :type iface: string
        """

        ifconfig_up(iface)

    def down(self, iface):
        """
        Bring an iface down.

        :param iface: Network interface, e.g. eth0
        :type iface: string
        """

        ifconfig_down(iface)

    def get_hostname(self):
        """
        Get hostname value.

        :return: Hostname
        :rtype: string
        """

        return subprocess.check_output('hostname', encoding='utf-8')

    def set_hostname(self, value):
        """
        Write new hostname in /etc/hostname.

        :param value: Hostname name
        :type value: string
        """

        with open('/etc/hostname', 'w') as f:
            f.write(value)
        subprocess.check_call(['hostname', value])
