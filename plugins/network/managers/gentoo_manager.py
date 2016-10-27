import subprocess
from jadi import component

import aj
from aj.plugins.augeas.api import Augeas
from aj.plugins.network.api import NetworkManager

from .ifconfig import ifconfig_up, ifconfig_down, ifconfig_get_ip, ifconfig_get_up


@component(NetworkManager)
class GentooNetworkManager(NetworkManager):
    path = '/etc/conf.d/net'
    aug_path = '/files' + path

    @classmethod
    def __verify__(cls):
        return aj.platform in ['gentoo']

    def __init__(self, context):
        NetworkManager.__init__(self, context)

    def get_augeas(self):
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
        ifaces = []
        aug = self.get_augeas()
        for key in aug.match('%s/*' % self.aug_path):
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

            route_key = '%s/routes_%s' % (self.aug_path, iface_name)
            if aug.match(route_key):
                routes = aug.get(route_key).strip('"').splitlines()
                for route in routes:
                    if route.strip().startswith('default via'):
                        iface['gateway'] = route.split()[-1]

        return ifaces

    def set_config(self, config):
        aug = self.get_augeas()
        for iface in config:
            if iface['addressing'] == 'dhcp':
                value = 'dhcp'
            else:
                value = iface['address']
                if iface.get('mask', None):
                    value += ' netmask %s' % iface['mask']
            aug.set('%s/config_%s' % (self.aug_path, iface['name']), '"%s"' % value)

            route_key = '%s/routes_%s' % (self.aug_path, iface['name'])
            if aug.match(route_key):
                routes = aug.get(route_key).strip('"').splitlines()
                routes = [route for route in routes if 'default via' not in route]
            else:
                routes = []
            if iface.get('gateway', None):
                routes.append('default via %s' % iface['gateway'])
            aug.set(route_key, '"%s"' % '\n'.join(routes))
        aug.save()

    def get_state(self, iface):
        return {
            'address': ifconfig_get_ip(iface),
            'up': ifconfig_get_up(iface),
        }

    def up(self, iface):
        subprocess.call(['/etc/init.d/net.%s' % iface, 'restart'])
        subprocess.call(['rc-update', 'add', 'net.%s' % iface, 'default'])

    def down(self, iface):
        subprocess.call(['/etc/init.d/net.%s' % iface, 'stop'])
        subprocess.call(['rc-update', 'delete', 'net.%s' % iface, 'default'])

    def get_hostname(self):
        return subprocess.check_output('hostname')

    def set_hostname(self, value):
        with open('/etc/hostname', 'w') as f:
            f.write(value)
        subprocess.check_call(['hostname', value])
