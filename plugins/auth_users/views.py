import aj
from aj.api import component
from aj.api.http import url, HttpPlugin

from aj.plugins.core.api.endpoint import endpoint
from aj.plugins.auth_users.api import UsersAuthenticationProvider


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.manager = UsersAuthenticationProvider(self.context)

    @url(r'/api/auth-users/set-password/(?P<username>.+)')
    @endpoint(api=True)
    def handle_api_set_password(self, http_context, username):
        password = http_context.body
        aj.config.load()
        aj.config.data['auth_users'][username]['password'] = self.manager.hash_password(password)
        aj.config.save()
