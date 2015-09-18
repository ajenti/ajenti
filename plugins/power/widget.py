from jadi import component
from aj.plugins.dashboard.api import Widget
from aj.plugins.power.api import PowerManager


@component(Widget)
class PowerWidget(Widget):
    id = 'power'
    name = _('Power state')
    template = '/power:resources/partial/widget.html'

    def __init__(self, context):
        Widget.__init__(self, context)
        self.manager = PowerManager.get(self.context)

    def get_value(self, config):
        return {
            'batteries': self.manager.get_batteries(),
            'adapters': self.manager.get_adapters(),
        }
