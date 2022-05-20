import json
import os
from jadi import component

import aj
from aj.auth import authorize
from aj.api.http import get, post, HttpPlugin
from aj.config import UserConfigService
from aj.auth import AuthenticationProvider, PermissionProvider, AuthenticationService

from aj.api.endpoint import endpoint, EndpointReturn


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/core/config')
    @endpoint(api=True)
    def handle_api_get_config(self, http_context):
        """
        Load the ajenti config file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of the ajenti config file
        :rtype: dict
        """

        if os.getuid() != 0:
            raise EndpointReturn(403)

        with authorize('core:config:read'):
            self.context.worker.reload_master_config()
            return aj.config.data

    @post(r'/api/core/config')
    @endpoint(api=True)
    def handle_api_post_config(self, http_context):
        """
        Save the ajenti config file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of the ajenti config file
        :rtype: dict
        """

        if os.getuid() != 0:
            raise EndpointReturn(403)

        with authorize('core:config:write'):
            data = json.loads(http_context.body.decode())
            aj.config.data.update(data)
            aj.config.save()
            self.context.worker.reload_master_config()
            return aj.config.data

    @get(r'/api/core/user-config')
    @endpoint(api=True)
    def handle_api_get_user_config(self, http_context):
        """
        Load the user config file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of the ajenti config file
        :rtype: dict
        """

        return UserConfigService.get(self.context).get_provider().data

    @post(r'/api/core/user-config')
    @endpoint(api=True)
    def handle_api_post_user_config(self, http_context):
        """
        Save the user config file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of the ajenti config file
        :rtype: dict
        """

        data = json.loads(http_context.body.decode())
        config = UserConfigService.get(self.context).get_provider()
        config.data.update(data)
        config.save()

    @get(r'/api/core/smtp-config')
    @endpoint(api=True)
    def handle_api_get_smtp_config(self, http_context):
        """
        Load the smtp config file without password.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of the ajenti config file without password
        :rtype: dict
        """

        if os.getuid() != 0:
            raise EndpointReturn(403)

        with authorize('core:config:read'):
            return aj.smtp_config.data

    @post(r'/api/core/smtp-config')
    @endpoint(api=True)
    def handle_api_post_smtp_config(self, http_context):
        """
        Save the smtp config file without password.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of the ajenti config file without password
        :rtype: dict
        """

        if os.getuid() != 0:
            raise EndpointReturn(403)

        with authorize('core:config:write'):
            data = json.loads(http_context.body.decode())
            aj.smtp_config.save(data)

    @get(r'/api/core/authentication-providers')
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
        auth_service_id =AuthenticationService.get(self.context).get_provider().id
        for p in AuthenticationProvider.all(self.context):
            r.append({
                'id': p.id,
                'name': p.name,
                'used': True if p.id == auth_service_id else False,
            })
        return r

    @get(r'/api/core/permissions')
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
