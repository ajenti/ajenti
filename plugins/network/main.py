from jadi import component

from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
                'attach': 'category:system',
                'id': 'network',
                'name': 'Network',
                'icon': 'plug',
                'url': '/view/network',
                'children': [],
            }
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'network:configure',
                'name': 'Configure network interfaces',
                'default': True,
            },
            {
                'id': 'network:updown',
                'name': 'Activate/deactivate network interfaces',
                'default': True,
            },
        ]
