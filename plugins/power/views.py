"""
MOdule to hande power management systems.
"""

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
        """
        Get system uptime.

        :param http_context: HttpContext
        :type http_context: Httpcontext
        :return: System uptime
        :rtype: float
        """

        return time.time() - psutil.boot_time()

    @url(r'/api/power/batteries')
    @endpoint(api=True)
    def handle_api_batteries(self, http_context):
        """
        For systems running on acpi battery, get the list of batteries.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of batteries
        :rtype: list
        """

        return self.manager.get_batteries()

    @url(r'/api/power/adapters')
    @endpoint(api=True)
    def handle_api_adapters(self, http_context):
        """
        For systems running on ac adapters, get the list of adapters.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of adapters
        :rtype: list
        """

        return self.manager.get_adapters()

    @url(r'/api/power/poweroff')
    @authorize('power:manage')
    @endpoint(api=True)
    def handle_api_poweroff(self, http_context):
        """
        Send power off signal to the manager.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        self.manager.poweroff()

    @url(r'/api/power/reboot')
    @authorize('power:manage')
    @endpoint(api=True)
    def handle_api_reboot(self, http_context):
        """
        Send reboot signal to the manager.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        self.manager.reboot()

    @url(r'/api/power/suspend')
    @authorize('power:manage')
    @endpoint(api=True)
    def handle_api_suspend(self, http_context):
        """
        Send suspend signal to the manager.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        self.manager.suspend()

    @url(r'/api/power/hibernate')
    @authorize('power:manage')
    @endpoint(api=True)
    def handle_api_hibernate(self, http_context):
        """
        Send hibernate signal to the manager.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        self.manager.hibernate()
