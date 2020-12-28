"""
User authentication provider based on the ajenti config file and permissions management.
"""

from jadi import component

import aj
from aj.api.http import url, HttpPlugin

from aj.api.endpoint import endpoint
from aj.plugins.auth_users.api import UsersAuthenticationProvider


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.manager = UsersAuthenticationProvider(self.context)

    @url(r'/api/auth-users/set-password/(?P<username>.+)')
    @endpoint(api=True)
    def handle_api_set_password(self, http_context, username):
        """
        Set user password in ajenti config file.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param username: Username
        :type username: string
        """

        password = http_context.body
        self.context.worker.reload_master_config()
        aj.config.data.setdefault('auth', {}).setdefault('users', {}).setdefault(username, {})['password'] = self.manager.hash_password(password)
        aj.config.save()
