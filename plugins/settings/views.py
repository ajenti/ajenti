import json

import aj
from aj.api import *
from aj.api.http import url, HttpPlugin

from aj.plugins.core.api.endpoint import endpoint


@component(HttpPlugin)
class Handler (HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/settings/config')
    @endpoint(api=True)
    def handle_api_config(self, http_context):
        if self.context.identity != 'root':
            return http_context.respond_forbidden()
        if http_context.method == 'GET':
            return aj.config.data
        if http_context.method == 'POST':
            data = json.loads(http_context.body)
            aj.config.data.update(data)
            aj.config.save()
