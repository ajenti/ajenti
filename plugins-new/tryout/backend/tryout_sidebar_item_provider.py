from jadi import component
from aj.plugins.core.api.sidebar import SidebarItemProvider

@component(SidebarItemProvider)
class SidebarItemProvider (SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
               {
                    'attach': 'category:general',
                    'name': 'Tryout',
                    'icon': 'bar-chart',
                    'url': '/view/tryout',
                    'children': []
               }
        ]
