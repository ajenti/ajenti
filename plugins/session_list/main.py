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
                'attach': 'category:tools',
                'id': 'session_list',
                'name': _('Session list'),
                'icon': 'fas fa-network-wired',
                'url': '/view/session_list/',
                'children': [],
            }
        ]
