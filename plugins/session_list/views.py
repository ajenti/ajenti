"""
Update the list of connected user. This need a communication between the worker
process and the root process.
"""

from jadi import component

from aj.api.http import url, HttpPlugin
# from aj.auth import authorize
from aj.api.endpoint import endpoint
import aj
import gevent

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/session_list/list')
    @endpoint(api=True)
    def handle_api_list_sessions(self, http_context):
        """
        Send an update request from the worker process to the root process in
        order to get an actual list of connected users and their details,
        stored in the var aj.sessions.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Dict of Session obj
        :rtype: dict
        """

        if http_context.method == 'GET':
            self.context.worker.update_sessionlist()
            gevent.sleep(1)
            return aj.sessions
            
