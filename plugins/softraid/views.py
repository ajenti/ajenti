"""
Module to parse the content of /proc/mdstat and show actual sotraid configuration.
"""

from jadi import component

from aj.api.http import get, HttpPlugin
# from aj.auth import authorize
from aj.api.endpoint import endpoint
from aj.plugins.softraid.softraid import RAIDManager

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/softraid/arrays')
    # @authorize('softraid:show')
    @endpoint(api=True)
    def handle_api_get_softraid(self, http_context):
        """
        Connector to the manager in order to retrieve a list of arrays.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of arrays
        :rtype: list
        """

        try:
            raid = RAIDManager()
            return raid.arrays
        except:
            return []

