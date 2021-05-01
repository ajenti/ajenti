from jadi import component

from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider
from .api import PackageManager


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        children = [{
            'attach': 'packages',
            'name': mgr.name,
            'icon': 'gift',
            'url': f'/view/packages/{mgr.id}',
            'children': [],
        } for mgr in PackageManager.all(self.context)]

        first_manager = PackageManager.all(self.context, ignore_exceptions=True)[0].id
        return [
            {
                'attach': 'category:system',
                'id': 'packages',
                'name': _('Packages'),
                'icon': 'gift',
                'url': f'/view/packages/{first_manager}',
                'children': children,
            }
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'packages:install',
                'name': _('Install/remove packages'),
                'default': True,
            },
        ]
