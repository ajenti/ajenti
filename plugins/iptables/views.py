from jadi import component

from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/iptables')
    @endpoint(api=True)
    def handle_api_get_iptables(self, http_context):
        pass

    @post(r'/api/iptables')
    @endpoint(api=True)
    def handle_api_post_iptables(self, http_context):
        pass
