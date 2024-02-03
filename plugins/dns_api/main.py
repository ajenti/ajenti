from jadi import component

from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:tools',
                'name': 'External DNS',
                'icon': 'globe',
                'url': '/view/dns_api',
                'children': []
            }
        ]

@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'dns_api:read',
                'name': _('List DNS entries via API'),
                'default': False,
            },
            {
                'id': 'dns_api:write',
                'name': _('Modify DNS entries via API'),
                'default': False,
            }
        ]
