from jadi import component

from aj.plugins.core.api.sidebar import SidebarItemProvider

@component(SidebarItemProvider)
class ShellSidebarItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': None,
                'id': 'category:general',
                'name': _('General'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:tools',
                'name': _('Tools'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:software',
                'name': _('Software'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:system',
                'name': _('System'),
                'children': [
                ]
            },
            {
                'attach': None,
                'id': 'category:other',
                'name': _('Other'),
                'children': [
                ]
            },
        ]
