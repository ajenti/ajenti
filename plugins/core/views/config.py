import json
from jadi import component

import aj
from aj.api.http import url, HttpPlugin
from aj.config import UserConfig
from aj.auth import AuthenticationProvider

from aj.api.endpoint import endpoint, EndpointReturn


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/core/config')
    @endpoint(api=True)
    def handle_api_config(self, http_context):
        if self.context.identity != 'root':
            raise EndpointReturn(403)
        if http_context.method == 'GET':
            self.context.worker.reload_master_config()
            return aj.config.data
        if http_context.method == 'POST':
            data = json.loads(http_context.body)
            aj.config.data.update(data)
            aj.config.save()
            return aj.config.data

    @url(r'/api/core/user-config')
    @endpoint(api=True)
    def handle_api_user_config(self, http_context):
        if http_context.method == 'GET':
            return UserConfig.get(self.context).data
        if http_context.method == 'POST':
            data = json.loads(http_context.body)
            config = UserConfig.get(self.context)
            config.data.update(data)
            config.save()

    @url(r'/api/core/authentication-providers')
    @endpoint(api=True)
    def handle_api_auth_providers(self, http_context):
        r = []
        for p in AuthenticationProvider.all(self.context):
            r.append({
                'id': p.id,
                'name': p.name,
            })
        return r
