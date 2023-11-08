import psutil
from jadi import component
from aj.plugins.dashboard.widget import Widget

@component(Widget)
class WidgetTemplate(Widget):
    id = 'templateWidget'
    name = _('TemplateWidget')

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        if not config:
            return 187