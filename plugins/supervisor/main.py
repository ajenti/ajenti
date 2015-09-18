from jadi import component
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
                'attach': 'category:software',
                'id': 'supervisor',
                'name': _('Supervisor'),
                'icon': 'play',
                'url': '/view/supervisor',
                'children': [],
            }
        ]
