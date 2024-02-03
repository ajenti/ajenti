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
                # category:tools, category:software, category:system, category:other
                'attach': 'category:software',
                'name': 'Docker',
                'icon': 'fab fa-docker',
                'url': '/view/docker',
                'children': []
            }
        ]

@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'docker:read',
                'name': _('List Docker containers, images and inspect'),
                'default': False,
            },
            {
                'id': 'docker:write',
                'name': _('Modify Docker containers, images'),
                'default': False,
            }
        ]