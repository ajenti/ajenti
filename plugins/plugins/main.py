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
                'attach': 'category:general',
                'name': _('Plugins'),
                'icon': 'th-large',
                'url': '/view/plugins',
                'children': [
                ]
            }
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'plugins:install',
                'name': _('Install plugins'),
                'default': False,
            },
            {
                'id': 'plugins:uninstall',
                'name': _('Uninstall plugins'),
                'default': False,
            },
            {
                'id': 'plugins:upgrade',
                'name': _('Upgrade Ajenti'),
                'default': False,
            },
        ]
