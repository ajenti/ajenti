import psutil

from jadi import component

from aj.plugins.dashboard.api import Widget


@component(Widget)
class TrafficWidget(Widget):
    id = 'traffic'
    name = _('Traffic')
    template = '/traffic:resources/partial/widget.html'
    config_template = '/traffic:resources/partial/widget.config.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        info = psutil.net_io_counters(pernic=True).get(config.get('interface', None), None)
        if not info:
            return None

        return {
            'tx': info.bytes_sent,
            'rx': info.bytes_recv,
        }
