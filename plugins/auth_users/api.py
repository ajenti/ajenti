import logging
import os
import scrypt
from jadi import component

import aj
from aj.auth import AuthenticationProvider


@component(AuthenticationProvider)
class UsersAuthenticationProvider(AuthenticationProvider):
    """
    Alternate authentication provider based on ajenti config file.
    """

    id = 'users'
    name = _('Custom users')

    def __init__(self, context):
        self.context = context
        aj.users.data.setdefault('users', {})

    def get_salt(self):
        return os.urandom(256)

    def hash_password(self, password, salt=None):
        """
        :rtype: str
        """
        password = password.decode('utf-8')
        if not salt:
            salt = self.get_salt()
        return scrypt.encrypt(salt, password, maxtime=1).hex()

    def authenticate(self, username, password):
        self.context.worker.reload_master_config()
        password = password.encode('utf-8')
        if username in aj.users.data['users']:
            user_hash = aj.users.data['users'][username]['password']
            try:
                scrypt.decrypt(bytes.fromhex(user_hash), password, maxtime=15, encoding=None)
                return True
            except scrypt.error as e:
                logging.debug('Auth failed: %s' % e)
                return False
        return False

    def authorize(self, username, permission):
        return aj.users.data['users'].get(username, {}).get('permissions', {}).get(permission['id'], permission['default'])

    def get_isolation_uid(self, username):
        return aj.users.data['users'][username]['uid']

    def get_isolation_gid(self, username):
        return None

    def get_profile(self, username):
        if not username:
            return {}
        return aj.users.data['users'][username]
