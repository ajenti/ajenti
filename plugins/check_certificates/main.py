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
                'id': 'check_cert',
                'name': _('Check certificates'),
                'icon': 'fas fa-certificate',
                'url': '/view/check_cert/certificates',
                'children': [],
            }
        ]
