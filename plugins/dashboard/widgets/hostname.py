import platform
from jadi import component

from aj.plugins.dashboard.api import Widget


@component(Widget)
class HostnameWidget(Widget):
    id = 'hostname'
    name = _('Hostname')
    template = '/dashboard:resources/partial/widgets/hostname.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        return platform.node()
