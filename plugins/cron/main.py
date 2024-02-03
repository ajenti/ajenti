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
                'attach': 'category:system',
                'name': 'Cron',
                'icon': 'clock-o',
                'url': '/view/cron',
                'children': []
            }
        ]

@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'crontab:read',
                'name': _('Read crontab jobs'),
                'default': False,
            },
            {
                'id': 'crontab:write',
                'name': _('Write jobs in crontab'),
                'default': False,
            },
        ]