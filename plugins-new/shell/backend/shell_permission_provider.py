from jadi import component
from aj.auth import PermissionProvider
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(PermissionProvider)
class ShellPermissionProvider (PermissionProvider):
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
