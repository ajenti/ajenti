from aj.plugins.core.api.sidebar import *


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
                'attach': 'category:system',
                'id': 'network',
                'name': 'Network',
                'icon': 'plug',
                'url': '/view/network',
                'children': [],
            }
        ]
