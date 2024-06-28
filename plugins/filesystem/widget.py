import psutil

from jadi import component
from aj.plugins.dashboard.api import Widget


@component(Widget)
class DiskWidget(Widget):
    id = 'disk'
    name = _('Disk space')
    template = '/filesystem:resources/partial/widget.html'
    config_template = '/filesystem:resources/partial/widget.config.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        parts = psutil.disk_partitions()
        usage = {x.mountpoint:psutil.disk_usage(x.mountpoint) for x in parts}
        mountpoint = config.get('mountpoint', None)
        if mountpoint is None:
            return {
                'total': sum(x.total for x in usage.values()),
                'free': sum(x.free for x in usage.values()),
                'used': sum(x.used for x in usage.values()),
            }
        if mountpoint in usage:
            return {
                'total': usage[mountpoint].total,
                'free': usage[mountpoint].free,
                'used': usage[mountpoint].used,
            }
        return {
            'total': None,
            'free': None,
            'used': None,
        }
