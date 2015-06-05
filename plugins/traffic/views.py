import psutil

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/traffic/interfaces')
    @endpoint(api=True)
    def handle_api_interfaces(self, http_context):
        return list(psutil.net_io_counters(pernic=True).keys())
