import json
import os
from jadi import component

import aj
from aj.auth import authorize
from aj.api.http import url, HttpPlugin
from aj.config import UserConfigService
from aj.auth import AuthenticationProvider, PermissionProvider

from aj.api.endpoint import endpoint, EndpointReturn


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/core/config')
    @endpoint(api=True)
    def handle_api_config(self, http_context):
        """
        Load (method get) and save (method post) the ajenti config file.
        Method GET.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of the ajenti config file
        :rtype: dict
        """

        if os.getuid() != 0:
            raise EndpointReturn(403)
        if http_context.method == 'GET':
            with authorize('core:config:read'):
                self.context.worker.reload_master_config()
                return aj.config.data
        if http_context.method == 'POST':
            with authorize('core:config:write'):
                data = json.loads(http_context.body.decode())
                aj.config.data.update(data)
                aj.config.save()
                self.context.worker.reload_master_config()
                return aj.config.data

    @url(r'/api/core/user-config')
    @endpoint(api=True)
    def handle_api_user_config(self, http_context):
        """
        Load (method get) and save (method post) the user config file.
        Method GET.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of the ajenti config file
        :rtype: dict
        """

        if http_context.method == 'GET':
            return UserConfigService.get(self.context).get_provider().data
        if http_context.method == 'POST':
            data = json.loads(http_context.body.decode())
            config = UserConfigService.get(self.context).get_provider()
            config.data.update(data)
            config.save()

    @url(r'/api/core/authentication-providers')
    @endpoint(api=True)
    def handle_api_auth_providers(self, http_context):
        """
        Load all authentication methods.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of authenticator, one per dict
        :rtype: list of dict
        """

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
        """
        Load all permissions ( api and sidebar ).

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of permissions
        :rtype: List of dict
        """

        r = []
        for p in PermissionProvider.all(self.context):
            r += p.provide()
        return r
