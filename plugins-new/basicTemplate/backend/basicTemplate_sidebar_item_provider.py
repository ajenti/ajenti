# pyflakes: disable-all
from jadi import component
from aj.plugins.core.api.sidebar import SidebarItemProvider

@component(SidebarItemProvider)
class BasicTemplateSideItemProvider (SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:general',
                'name': 'BasicTemplate',
                'icon': 'bar-chart',
                'url': '/view/basicTemplate',
                'children': [
                ]
            }
        ]
