import subprocess

import aj
from jadi import component
from aj.plugins.augeas.api import Augeas
from aj.plugins.network.api import NetworkManager

from .ifconfig import ifconfig_up, ifconfig_down, ifconfig_get_ip, ifconfig_get_up


@component(NetworkManager)
class DebianNetworkManager(NetworkManager):
    path = '/etc/network/interfaces'
    aug_path = '/files' + path

    @classmethod
    def __verify__(cls):
        return aj.platform in ['debian']

    def __init__(self, context):
        NetworkManager.__init__(self, context)

    def get_augeas(self):
        aug = Augeas(modules=[{
            'name': 'Interfaces',
            'lens': 'Interfaces.lns',
            'incl': [
                self.path,
                self.path + '.d/*',
            ]
        }])
        aug.load()
        return aug

    def get_config(self):
        aug = self.get_augeas()
        ifaces = []
        for path in aug.match(self.aug_path + '/iface[*]'):
            iface = {
                'name': aug.get(path),
                'family': aug.get(path + '/family'),
                'addressing': aug.get(path + '/method'),
                'address': aug.get(path + '/address'),
                'mask': aug.get(path + '/netmask'),
                'gateway': aug.get(path + '/gateway'),
                'hwaddress': aug.get(path + '/hwaddress'),
                'mtu': aug.get(path + '/mtu'),
                'scope': aug.get(path + '/scope'),
                'metric': aug.get(path + '/metric'),
                'client': aug.get(path + '/client'),
                'pre_up_script': aug.get(path + '/pre-up'),
                'pre_down_script': aug.get(path + '/pre-down'),
                'up_script': aug.get(path + '/up'),
                'down_script': aug.get(path + '/down'),
                'post_up_script': aug.get(path + '/post-up'),
                'post_down_script': aug.get(path + '/post-down'),
            }
            ifaces.append(iface)
        return ifaces

    def set_config(self, config):
        aug = self.get_augeas()
        for index, iface in enumerate(config):
            path = self.aug_path + ('/iface[%i]' % (index + 1))
            aug.setd(path + '/family', iface['family'])
            aug.setd(path + '/method', iface['addressing'])
            aug.setd(path + '/address', iface['address'])
            aug.setd(path + '/netmask', iface['mask'])
            aug.setd(path + '/gateway', iface['gateway'])
            aug.setd(path + '/hwaddress', iface['hwaddress'])
            aug.setd(path + '/mtu', iface['mtu'])
            aug.setd(path + '/scope', iface['scope'])
            aug.setd(path + '/metric', iface['metric'])
            aug.setd(path + '/client', iface['client'])
            aug.setd(path + '/pre-up', iface['pre_up_script'])
            aug.setd(path + '/pre-down', iface['pre_down_script'])
            aug.setd(path + '/up', iface['up_script'])
            aug.setd(path + '/down', iface['down_script'])
            aug.setd(path + '/post-up', iface['post_up_script'])
            aug.setd(path + '/post-down', iface['post_down_script'])
        aug.save()

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
        return subprocess.check_output('hostname')

    def set_hostname(self, value):
        with open('/etc/hostname', 'w') as f:
            f.write(value)
        subprocess.check_call(['hostname', value])
