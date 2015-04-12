from aj.api import component
from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
                'attach': 'category:system',
                'id': 'datetime',
                'name': 'Date & time',
                'icon': 'clock-o',
                'url': '/view/datetime',
                'children': [],
            }
        ]
