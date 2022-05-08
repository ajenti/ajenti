"""
Retrieve I/O stats for all network interfaces.
"""

import psutil

from jadi import component
from aj.api.http import get, HttpPlugin
from aj.api.endpoint import endpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/traffic/interfaces')
    @endpoint(api=True)
    def handle_api_interfaces(self, http_context):
        """
        Get list of network interfaces and I/O stats.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of network interfaces and I/O stats
        :rtype: list
        """

        return list(psutil.net_io_counters(pernic=True).keys())
