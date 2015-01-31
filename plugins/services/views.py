import aj
from aj.api import *
from aj.api.http import url, HttpPlugin

from aj.plugins.core.api.endpoint import endpoint
from aj.plugins.services.api import ServiceManager


@component(HttpPlugin)
class Handler (HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.managers = dict((x.id, x) for x in ServiceManager.all(self.context))

    def __service_to_json(self, service):
        return {
            'id': service.id,
            'name': service.name,
            'state': service.state,
            'running': service.running,
            'managerId': service.manager.id,
        }

    @url(r'/api/services/managers')
    @endpoint(api=True)
    def handle_api_managers(self, http_context):
        return [
            {
                'id': mgr.id,
                'name': mgr.name,
            } for mgr in self.managers.values()
        ]

    @url(r'/api/services/list/(?P<manager_id>\w+)')
    @endpoint(api=True)
    def handle_api_list(self, http_context, manager_id=None):
        return [self.__service_to_json(service) for service in self.managers[manager_id].list()]

    @url(r'/api/services/get/(?P<manager_id>\w+)/(?P<service_id>.+)')
    @endpoint(api=True)
    def handle_api_get(self, http_context, manager_id=None, service_id=None):
        return self.__service_to_json(self.managers[manager_id].get(service_id))

    @url(r'/api/services/do/(?P<operation>\w+)/(?P<manager_id>\w+)/(?P<service_id>.+)')
    @endpoint(api=True)
    def handle_api_operate(self, http_context, manager_id=None, operation=None, service_id=None):
        if operation not in ['start', 'stop', 'restart']:
            return
        getattr(self.managers[manager_id], operation)(service_id)
