from aj.plugins.core.api.sidebar import *


@component(SidebarItemProvider)
class ItemProvider (SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:tools',
                'name': 'Notepad',
                'icon': 'pencil',
                'url': '/view/notepad',
                'children': [
                ]
            }
        ]