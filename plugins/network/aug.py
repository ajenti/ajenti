from jadi import component
from aj.plugins.augeas.api import AugeasEndpoint, Augeas


@component(AugeasEndpoint)
class ResolvConfEndpoint(AugeasEndpoint):
    id = 'resolv'

    def get_augeas(self):
        return Augeas(modules=[{
            'name': 'Resolv',
            'lens': 'Resolv.lns',
            'incl': [
                '/etc/resolv.conf',
            ]
        }])

    def get_root_path(self):
        return '/files/etc/resolv.conf'


@component(AugeasEndpoint)
class HostsEndpoint(AugeasEndpoint):
    id = 'hosts'

    def get_augeas(self):
        return Augeas(modules=[{
            'name': 'Hosts',
            'lens': 'Hosts.lns',
            'incl': [
                '/etc/hosts',
            ]
        }])

    def get_root_path(self):
        return '/files/etc/hosts'
