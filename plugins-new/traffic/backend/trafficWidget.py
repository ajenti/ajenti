import psutil
from jadi import component
from aj.plugins.dashboard.widget import Widget

@component(Widget)
class TrafficWidget(Widget):
    id = 'traffic'
    name = _('Traffic')

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        if not config:
            return None

        info = psutil.net_io_counters(pernic=True).get(config.get('interface', None), None)
        if not info:
            return None

        return {
            'bytesSent': info.bytes_sent,
            'bytesReceived': info.bytes_recv,
        }
