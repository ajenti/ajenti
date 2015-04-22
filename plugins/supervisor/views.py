from datetime import datetime
import subprocess
import time

from jadi import component
from aj.api.http import url, HttpPlugin

from aj.api.endpoint import endpoint, EndpointError


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/datetime/tz/get')
    @endpoint(api=True)
    def handle_api_tz_get(self, http_context):
        return self.manager.get_tz()

    @url(r'/api/datetime/tz/set/(?P<tz>.+)')
    @endpoint(api=True)
    def handle_api_tz_set(self, http_context, tz=None):
        return self.manager.set_tz(tz)

    @url(r'/api/datetime/tz/list')
    @endpoint(api=True)
    def handle_api_tz_list(self, http_context):
        return self.manager.list_tz()

    @url(r'/api/datetime/time/get')
    @endpoint(api=True)
    def handle_api_time_get(self, http_context):
        return int(time.time())

    @url(r'/api/datetime/time/set/(?P<time>.+)')
    @endpoint(api=True)
    def handle_api_time_set(self, http_context, time=None):
        subprocess.call(['date', datetime.fromtimestamp(int(time)).strftime('%m%d%H%M%Y')])

    @url(r'/api/datetime/time/sync')
    @endpoint(api=True)
    def handle_api_time_sync(self, http_context):
        try:
            subprocess.check_call(['ntpdate', '0.pool.ntp.org'])
        except Exception as e:
            raise EndpointError(e)
        return int(time.time())
