from jadi import component
from aj.plugins.dashboard.api import Widget


@component(Widget)
class ScriptWidget(Widget):
    id = 'script'
    name = _('Script')
    template = '/terminal:resources/partial/widget.html'
    config_template = '/terminal:resources/partial/widget.config.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        pass
