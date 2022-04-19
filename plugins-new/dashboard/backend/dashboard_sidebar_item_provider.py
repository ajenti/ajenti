from jadi import component
from aj.plugins.core.api.sidebar import SidebarItemProvider

@component(SidebarItemProvider)
class DashboardSidebarItemProvider (SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:general',
                'name': _('Dashboard'),
                'icon': 'bar-chart',
                'url': '/view/dashboard',
                'children': [
                ]
            }
        ]
