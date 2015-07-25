import psutil
import time

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint
from aj.plugins.power.api import PowerManager


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.manager = PowerManager.get(self.context)

    @url(r'/api/power/uptime')
    @endpoint(api=True)
    def handle_api_uptime(self, http_context):
        return time.time() - psutil.boot_time()

    @url(r'/api/power/batteries')
    @endpoint(api=True)
    def handle_api_batteries(self, http_context):
        return self.manager.get_batteries()

    @url(r'/api/power/adapters')
    @endpoint(api=True)
    def handle_api_adapters(self, http_context):
        return self.manager.get_adapters()

    @url(r'/api/power/poweroff')
    @authorize('power:manage')
    @endpoint(api=True)
    def handle_api_poweroff(self, http_context):
        self.manager.poweroff()

    @url(r'/api/power/reboot')
    @authorize('power:manage')
    @endpoint(api=True)
    def handle_api_reboot(self, http_context):
        self.manager.reboot()

    @url(r'/api/power/suspend')
    @authorize('power:manage')
    @endpoint(api=True)
    def handle_api_suspend(self, http_context):
        self.manager.suspend()

    @url(r'/api/power/hibernate')
    @authorize('power:manage')
    @endpoint(api=True)
    def handle_api_hibernate(self, http_context):
        self.manager.hibernate()
