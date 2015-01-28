from aj.plugins.core.api.sidebar import *


@component(SidebarItemProvider)
class ItemProvider (SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': None,
                'id': 'category:general',
                'name': 'General',
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:system',
                'name': 'System',
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:tools',
                'name': 'Tools',
                'children': [
                ]
            },
        ]