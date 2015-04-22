from jadi import component

from aj.plugins.core.api.sidebar import SidebarItemProvider

from .api import ServiceManager


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        children = [{
            'attach': 'services',
            'name': mgr.name,
            'icon': 'cog',
            'url': '/view/services/%s' % mgr.id,
            'children': [],
        } for mgr in ServiceManager.all(self.context)]

        return [
            {
                'attach': 'category:software',
                'name': 'Services',
                'icon': 'cogs',
                'url': '/view/services',
                'children': children
            }
        ]
