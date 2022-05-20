"""
Manage a widget page and refresh all values automatically.
"""

from jadi import component

from aj.api.http import get, post, HttpPlugin

from aj.api.endpoint import endpoint
from aj.plugins.dashboard.api import Widget


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.widgets = {x.id:x for x in Widget.all(self.context)}

    @get(r'/api/dashboard/widgets')
    @endpoint(api=True)
    def handle_api_widgets(self, http_context):
        """
        Connector to get all available widgets values.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Data widgets as dict in a list
        :rtype: list of dict
        """

        return [
            {
                'id': w.id,
                'name': w.name,
                'template': w.template,
                'config_template': w.config_template,
            } for w in self.widgets.values()
        ]

    @post(r'/api/dashboard/widgets-values')
    @endpoint(api=True)
    def handle_api_get_values(self, http_context):
        """
        Refresh data values for all widgets.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of values as dict
        :rtype: list of dict
        """

        data = http_context.json_body()
        return [
            {
                'id': rq['id'],
                'data': self.widgets[rq['typeId']].get_value(rq['config']),
            } for rq in data
            if rq['typeId'] in self.widgets
        ]
