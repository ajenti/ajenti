"""
Module to set, sync and display current time zone.
"""

import logging
import subprocess
import time
from datetime import datetime
from jadi import component

from aj.api.http import url, HttpPlugin
from aj.auth import authorize
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.datetime.api import TZManager


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.manager = TZManager.any(self.context)

    @url(r'/api/datetime/tz/get')
    @endpoint(api=True)
    def handle_api_tz_get(self, http_context):
        """
        Get current time zone.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Current time zone and offset
        :rtype: dict
        """

        time.tzset()
        return {
            'tz': self.manager.get_tz(),
            'offset': self.manager.get_offset(),
        }

    @url(r'/api/datetime/tz/set/(?P<tz>.+)')
    @authorize('datetime:write')
    @endpoint(api=True)
    def handle_api_tz_set(self, http_context, tz=None):
        """
        Connector to set time zone on the server through the manager.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param tz: Time zone e.g. Europe/London
        :type tz: string
        """

        return self.manager.set_tz(tz)

    @url(r'/api/datetime/tz/list')
    @endpoint(api=True)
    def handle_api_tz_list(self, http_context):
        """
        Connector to list all availables time zones on the server.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of time zones
        :rtype: list
        """

        return self.manager.list_tz()

    @url(r'/api/datetime/time/get')
    @endpoint(api=True)
    def handle_api_time_get(self, http_context):
        """
        Get current time.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Rounded time since EPOCH
        :rtype: integer
        """

        return int(time.time())

    @url(r'/api/datetime/time/set/(?P<time>.+)')
    @authorize('datetime:write')
    @endpoint(api=True)
    def handle_api_time_set(self, http_context, time=None):
        """
        Set time on the server through date command.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param time: Time from frontend
        :type time: float
        """

        subprocess.call(['date', datetime.fromtimestamp(int(time)).strftime('%m%d%H%M%Y')])
        try:
            subprocess.call(['hwclock', '--systohc'])
        except FileNotFoundError as e:
            logging.warning('No hwclock utility available, not setting hardware clock')

    @url(r'/api/datetime/time/sync')
    @authorize('datetime:write')
    @endpoint(api=True)
    def handle_api_time_sync(self, http_context):
        """
        Sync time with ntpdate and return the correct time.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Right time
        :rtype: integer
        """

        if subprocess.call(['which', 'ntpdate']) != 0:
            raise EndpointError(_('ntpdate utility is not installed'))

        try:
            subprocess.check_call(['ntpdate', '-u', '0.pool.ntp.org'])
        except Exception as e:
            raise EndpointError(e)
        return int(time.time()-time.timezone)
