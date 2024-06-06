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
                'name': 'Filesystem',
                'icon': 'hdd',
                'url': '/view/fstab',
                'children': []
            }
        ]

@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'fstab:mount:read',
                'name': _('List mounts'),
                'default': False,
            },
            {
                'id': 'fstab:mount:umount',
                'name': _('Umount a device'),
                'default': False,
            },
            {
                'id': 'fstab:read',
                'name': _('Read fstab file'),
                'default': False,
            },
            {
                'id': 'fstab:write',
                'name': _('Write fstab file'),
                'default': False,
            },
        ]
