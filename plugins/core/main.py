from ajenti.plugins.core.api.sidebar import *


@component(SidebarItemProvider)
class ItemProvider (SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': None,
                'id': 'category:tools',
                'icon': 'cogs',
                'name': 'Tools',
                'children': [
                ]
            }
        ]
        '''
                            {
                        'name': 'Home',
                        'icon': 'home',
                        'url': '/view/',
                        'children': [
                        ]
                    }
        '''