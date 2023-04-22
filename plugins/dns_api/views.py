from jadi import component

from aj.api.http import get, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/dns_api')
    @endpoint(api=True)
    def handle_api_example_dns_api(self, http_context):
        pass
