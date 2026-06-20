from jadi import component

from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(PermissionProvider)
class Permissions(PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'iptables:read',
                'name': _('Read iptables rules'),
                'default': False,
            },
            {
                'id': 'iptables:write',
                'name': _('Modify iptables rules'),
                'default': False,
            },
        ]


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:software',
                'name': 'Iptables',
                'icon': 'ban',
                'url': '/view/iptables',
                'children': []
            }
        ]
