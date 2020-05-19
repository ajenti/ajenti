from jadi import component

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
import aj
import gevent

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/session_list/list')
    @endpoint(api=True)
    def handle_api_list_sessions(self, http_context):
        if http_context.method == 'GET':
            self.context.worker.update_sessionlist()
            gevent.sleep(1)
            return aj.sessions
            
