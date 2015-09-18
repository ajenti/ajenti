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
                'attach': None,
                'id': 'category:general',
                'name': _('General'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:tools',
                'name': _('Tools'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:software',
                'name': _('Software'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:system',
                'name': _('System'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:other',
                'name': _('Other'),
                'children': [
                ]
            },
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        sidebar_perms = [
            {
                'id': 'sidebar:view:%s' % item['url'],
                'name': item['name'],
                'default': True,
            }
            for provider in SidebarItemProvider.all(self.context)
            for item in provider.provide()
            if 'url' in item
        ]
        return [
            {
                'id': 'core:config:read',
                'name': _('Read configuration file'),
                'default': True,
            },
            {
                'id': 'core:config:write',
                'name': _('Write configuration file'),
                'default': True,
            },
        ] + sidebar_perms
