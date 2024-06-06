import platform
from jadi import component
from aj.plugins.dashboard.widget import Widget

@component(Widget)
class HostnameWidget(Widget):
    id = 'hostname'
    name = _('Hostname')

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        return platform.node()
