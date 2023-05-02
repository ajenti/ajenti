from jadi import component

from aj.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:tools',
                'name': 'External DNS',
                'icon': 'globe',
                'url': '/view/dns_api',
                'children': []
            }
        ]
