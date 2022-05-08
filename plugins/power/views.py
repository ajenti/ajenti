"""
MOdule to hande power management systems.
"""

import psutil
import time

from jadi import component
from aj.api.http import get, post, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint
from aj.plugins.power.api import PowerManager


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.manager = PowerManager.get(self.context)

    @get(r'/api/power/uptime')
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

    @get(r'/api/power/batteries')
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

    @get(r'/api/power/adapters')
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

    @post(r'/api/power/command_power')
    @authorize('power:manage')
    @endpoint(api=True)
    def handle_api_poweroff(self, http_context):
        """
        Send command signal to the manager.
        Valid commands are poweroff, reboot, suspend and hibernate.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        command = http_context.json_body()['command']
        if command in ['poweroff', 'reboot', 'suspend', 'hibernate']:
            method = getattr(self.manager, command)
            method()
        else:
            http_context.respond_not_found()
