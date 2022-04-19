import psutil
from jadi import component
from aj.plugins.dashboard.widget import Widget

@component(Widget)
class MemoryWidget(Widget):
    id = 'memory'
    name = _('Memory usage')

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        v = psutil.virtual_memory()
        return {
            'used': v.total - v.available,
            'free': v.available,
            'total': v.total
        }
