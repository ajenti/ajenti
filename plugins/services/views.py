from jadi import component
from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.services.api import ServiceManager, ServiceOperationError


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.managers = dict((x.id, x) for x in ServiceManager.all(self.context))

    def __service_to_json(self, svc):
        return {
            'id': svc.id,
            'name': svc.name,
            'state': svc.state,
            'running': svc.running,
            'managerId': svc.manager.id,
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
        return [self.__service_to_json(svc) for svc in self.managers[manager_id].list()]

    @url(r'/api/services/get/(?P<manager_id>\w+)/(?P<service_id>.+)')
    @endpoint(api=True)
    def handle_api_get(self, http_context, manager_id=None, service_id=None):
        return self.__service_to_json(self.managers[manager_id].get_service(service_id))

    @url(r'/api/services/do/(?P<operation>\w+)/(?P<manager_id>\w+)/(?P<service_id>.+)')
    @authorize('services:manage')
    @endpoint(api=True)
    def handle_api_operate(self, http_context, manager_id=None, operation=None, service_id=None):
        if operation not in ['start', 'stop', 'restart']:
            return
        try:
            getattr(self.managers[manager_id], operation)(service_id)
        except ServiceOperationError as e:
            raise EndpointError(e)
