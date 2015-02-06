from aj.api import *
from aj.plugins.dashboard.api import Widget
from aj.plugins.services.api import ServiceManager


@component(Widget)
class ServiceWidget (Widget):
    id = 'service'
    name = 'Service'
    template = '/services:resources/partial/widget.html'
    config_template = '/services:resources/partial/widget.config.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        for mgr in ServiceManager.all(self.context):
            if mgr.id == config.get('manager_id', None):
                svc = mgr.get(config.get('service_id', None))
                return {
                    'id': svc.id,
                    'name': svc.name,
                    'managerId': svc.manager.id,
                    'state': svc.state,
                    'isRunning': svc.running,
                }
