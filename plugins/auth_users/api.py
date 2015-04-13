import logging
import os
import scrypt

import aj
from aj.api import component
from aj.auth import AuthenticationProvider


@component(AuthenticationProvider)
class UsersAuthenticationProvider(AuthenticationProvider):
    id = 'users'
    name = 'Custom users'

    def __init__(self, context):
        self.context = context
        aj.config.data.setdefault('auth_users', {
            'root': {
                'uid': 0,
                'password': self.hash_password('admin')
            }
        })

    def get_salt(self):
        return os.urandom(256)

    def hash_password(self, password, salt=None):
        """
        :rtype: str
        """
        password = password.encode('utf-8')
        if not salt:
            salt = self.get_salt()
        return scrypt.encrypt(salt, password, maxtime=1).encode('hex')

    def authenticate(self, username, password):
        aj.config.load()
        password = password.encode('utf-8')
        if username in aj.config.data['auth_users']:
            hash = aj.config.data['auth_users'][username]['password']
            try:
                scrypt.decrypt(hash.decode('hex'), password, maxtime=2)
                return True
            except scrypt.error as e:
                logging.debug(e)
                return False
        return False

    def get_isolation_uid(self, username):
        return aj.config.data['auth_users'][username]['uid']
