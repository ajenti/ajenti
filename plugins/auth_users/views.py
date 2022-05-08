"""
User authentication provider based on the ajenti config file and permissions management.
"""

import os
import json
from jadi import component

import aj
from aj.auth import authorize
from aj.api.http import get, post, HttpPlugin

from aj.api.endpoint import endpoint, EndpointReturn
from aj.plugins.auth_users.api import UsersAuthenticationProvider


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.manager = UsersAuthenticationProvider(self.context)

    @post(r'/api/auth-users/password/(?P<username>.+)')
    @endpoint(api=True)
    def handle_api_set_password(self, http_context, username):
        """
        Set user password in ajenti config file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param username: Username
        :type username: string
        """

        password = http_context.body
        self.context.worker.reload_master_config()
        aj.users.data.setdefault('users', {}).setdefault(username, {})['password'] = self.manager.hash_password(password)
        aj.users.save()

    @get(r'/api/auth-users/config')
    @endpoint(api=True)
    def handle_api_users_get_config(self, http_context):
        """
        Load the ajenti users config file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of the ajenti users config file
        :rtype: dict
        """

        if os.getuid() != 0:
            raise EndpointReturn(403)

        with authorize('core:config:read'):
            self.context.worker.reload_master_config()
            return aj.users.data

    @post(r'/api/auth-users/config')
    @endpoint(api=True)
    def handle_api_users_set_config(self, http_context):
        """
        Save the ajenti users config file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Content of the ajenti users config file
        :rtype: dict
        """

        if os.getuid() != 0:
            raise EndpointReturn(403)

        with authorize('core:config:write'):
            data = json.loads(http_context.body.decode())
            aj.users.data.update(data)
            aj.users.save()
            self.context.worker.reload_master_config()
            return aj.users.data
