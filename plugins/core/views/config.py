import json
import os
from jadi import component

import aj
from aj.auth import authorize
from aj.api.http import url, HttpPlugin
from aj.config import UserConfig
from aj.auth import AuthenticationProvider, PermissionProvider

from aj.api.endpoint import endpoint, EndpointReturn


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/core/config')
    @endpoint(api=True)
    def handle_api_config(self, http_context):
        if os.getuid() != 0:
            raise EndpointReturn(403)
        if http_context.method == 'GET':
            with authorize('core:config:read'):
                self.context.worker.reload_master_config()
                return aj.config.data
        if http_context.method == 'POST':
            with authorize('core:config:write'):
                data = json.loads(http_context.body)
                aj.config.data.update(data)
                aj.config.save()
                self.context.worker.reload_master_config()
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

    @url(r'/api/core/permissions')
    @endpoint(api=True)
    def handle_api_permissions(self, http_context):
        r = []
        for p in PermissionProvider.all(self.context):
            r += p.provide()
        return r
