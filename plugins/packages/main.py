from aj.plugins.core.api.sidebar import *

from aj.plugins.packages.api import PackageManager


@component(SidebarItemProvider)
class ItemProvider (SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        children = [{
            'attach': 'packages',
            'name': mgr.name,
            'icon': 'gift',
            'url': '/view/packages/%s' % mgr.id,
            'children': [],
        } for mgr in PackageManager.all(self.context)]
        return [
            {
                'attach': 'category:system',
                'id': 'packages',
                'name': 'Packages',
                'icon': 'gift',
                'url': '/view/packages/%s' % PackageManager.all(self.context)[0].id,
                'children': children,
            }
        ]
