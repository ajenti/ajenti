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
                'id': 'datetime',
                'name': _('Date & time'),
                'icon': 'clock-o',
                'url': '/view/datetime',
                'children': [],
            }
        ]


@component(PermissionProvider)
class Permissions(PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'datetime:write',
                'name': _('Change date and time'),
                'default': True,
            },
        ]
