import subprocess
from jadi import component

import aj
from aj.plugins.augeas.api import Augeas
from aj.plugins.network.api import NetworkManager

from .ifconfig import ifconfig_get_ip, ifconfig_get_up


@component(NetworkManager)
class GentooNetworkManager(NetworkManager):
    path = '/etc/conf.d/net'
    aug_path = '/files' + path

    @classmethod
    def __verify__(cls):
        """
        Verify if this manager is relevant.

        :return: bool
        :rtype: bool
        """

        return aj.platform in ['gentoo']

    def __init__(self, context):
        NetworkManager.__init__(self, context)

    def get_augeas(self):
        """
        Read the content of interfaces config files through augeas.

        :return: Augeas object
        :rtype: augeas
        """

        aug = Augeas(modules=[{
            'name': 'Shellvars',
            'lens': 'Shellvars.lns',
            'incl': [
                self.path,
            ]
        }])
        aug.load()
        return aug

    def get_config(self):
        """
        Parse the content of interfaces config files through augeas.

        :return: List of iface informations, one iface per dict
        :rtype: list of dict
        """

        ifaces = []
        aug = self.get_augeas()
        for key in aug.match(f'{self.aug_path}/*'):
            if 'config_' not in key:
                continue
            iface_name = key.split('_')[-1]
            iface = {
                'name': iface_name,
                'family': 'inet',
            }
            value = aug.get(key).strip('"')
            if value == 'dhcp':
                iface['addressing'] = 'dhcp'
            else:
                iface['addressing'] = 'static'
                tokens = value.split()
                iface['address'] = tokens.pop(0)
                while len(tokens):
                    key = tokens.pop(0)
                    value = tokens.pop(0)
                    if key == 'netmask':
                        iface['mask'] = value
            ifaces.append(iface)

            route_key = f'{self.aug_path}/routes_{iface_name}'
            if aug.match(route_key):
                routes = aug.get(route_key).strip('"').splitlines()
                for route in routes:
                    if route.strip().startswith('default via'):
                        iface['gateway'] = route.split()[-1]

        return ifaces

    def set_config(self, config):
        """
        Set the new config in the config file through augeas.

        :param config: List of iface informations, one dict per iface
        :type config: list of dict
        """

        aug = self.get_augeas()
        for iface in config:
            if iface['addressing'] == 'dhcp':
                value = 'dhcp'
            else:
                value = iface['address']
                if iface.get('mask', None):
                    value += f' netmask {iface["mask"]}'
            aug.set(f'{self.aug_path}/config_{iface["name"]}', f'"{value}"')

            route_key = f'{self.aug_path}/routes_{iface["name"]}'
            if aug.match(route_key):
                routes = aug.get(route_key).strip('"').splitlines()
                routes = [route for route in routes if 'default via' not in route]
            else:
                routes = []
            if iface.get('gateway', None):
                routes.append(f'default via {iface["gateway"]}')
            route_join = '\n'.join(routes)
            aug.set(route_key, f'"{route_join}"')
        aug.save()

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

        subprocess.call([f'/etc/init.d/net.{iface}', 'restart'])
        subprocess.call(['rc-update', 'add', f'net.{iface}', 'default'])

    def down(self, iface):
        """
        Bring an iface down.

        :param iface: Network interface, e.g. eth0
        :type iface: string
        """

        subprocess.call([f'/etc/init.d/net.{iface}', 'stop'])
        subprocess.call(['rc-update', 'delete', f'net.{iface}', 'default'])

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
