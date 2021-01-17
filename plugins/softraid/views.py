"""
Module to parse the content of /proc/mdstat and show actual sotraid configuration.
"""

from jadi import component

from aj.api.http import url, HttpPlugin
# from aj.auth import authorize
from aj.api.endpoint import endpoint
from aj.plugins.softraid.softraid import RAIDManager

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/softraid')
    # @authorize('softraid:show')
    @endpoint(api=True)
    def handle_api_get_softraid(self, http_context):
        """
        Connector to the manager in order to retrieve a list of arrays.
        Method GET.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of arrays
        :rtype: list
        """

        if http_context.method == 'GET':
            try:
                raid = RAIDManager()
                return raid.arrays
            except:
                return []

