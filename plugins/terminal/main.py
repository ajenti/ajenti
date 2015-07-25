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
                'name': 'Terminal',
                'icon': 'terminal',
                'url': '/view/terminal',
                'children': []
            }
        ]

@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'terminal:scripts',
                'name': 'Run arbitrary scripts',
                'default': True,
            },
            {
                'id': 'terminal:open',
                'name': 'Open shell terminals',
                'default': True,
            },
        ]
