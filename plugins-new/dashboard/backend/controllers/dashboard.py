"""
Manages the general widget HTTP requests.
"""

from jadi import component
from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.plugins.dashboard.widget import Widget


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.widgets = {x.id:x for x in Widget.all(self.context)}

    @url(r'/api/dashboard/widget-types')
    @endpoint(api=True)
    def handle_api_widget_types(self, http_context):
        """
        Gets all available widgets types.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: All available widget types as dict in a list
        :rtype: list of dict
        """

        return [
            {
                'id': w.id,
                'name': w.name,
            } for w in self.widgets.values()
        ]

    @url(r'/api/dashboard/widget-values')
    @endpoint(api=True)
    def handle_api_widget_values(self, http_context):
        """
        Gets values for all widgets defined in the request.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of widget values as dict
        :rtype: list of dict
        """

        data = http_context.json_body()
        return [
            {
                'widgetId': rq['widgetId'],
                'widgetValues': self.widgets[rq['widgetTypeId']].get_value(rq['widgetConfig']),
            } for rq in data
            if rq['widgetTypeId'] in self.widgets
        ]
