import json
from jadi import component

from aj.api.http import url, HttpPlugin

from aj.api.endpoint import endpoint
from aj.plugins.dashboard.api import Widget


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.widgets = dict((x.id, x) for x in Widget.all(self.context))

    @url(r'/api/dashboard/widgets')
    @endpoint(api=True)
    def handle_api_widgets(self, http_context):
        return [
            {
                'id': w.id,
                'name': w.name,
                'template': w.template,
                'config_template': w.config_template,
            } for w in self.widgets.values()
        ]

    @url(r'/api/dashboard/get-values')
    @endpoint(api=True)
    def handle_api_get_values(self, http_context):
        data = http_context.json_body()
        return [
            {
                'id': rq['id'],
                'data': self.widgets[rq['typeId']].get_value(rq['config']),
            } for rq in data
            if rq['typeId'] in self.widgets
        ]
