import logging
import os
import pwd
import yaml
import stat
import scrypt
from jadi import component

import aj
from aj.auth import AuthenticationProvider
from aj.config import UserConfigProvider


@component(AuthenticationProvider)
class UsersAuthenticationProvider(AuthenticationProvider):
    """
    Alternate authentication provider based on ajenti config file.
    """

    id = 'users'
    name = _('Custom users')
    pw_reset = True

    def __init__(self, context):
        self.context = context

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
            user_hash = aj.users.data['users'][username].get('password', '')
            try:
                scrypt.decrypt(bytes.fromhex(user_hash), password, maxtime=15, encoding=None)
                return True
            except scrypt.error as e:
                logging.debug(f'Auth failed: {e}')
                return False
        return False

    def authorize(self, username, permission):
        return aj.users.data['users'].get(username, {}).get('permissions', {}).get(permission['id'], permission['default'])

    def prepare_environment(self, username):
        pass

    def get_isolation_uid(self, username):
        try:
            uid = aj.users.data['users'][username]['uid']
            return uid
        except KeyError:
            return pwd.getpwnam(aj.config.data['restricted_user']).pw_uid

    def get_isolation_gid(self, username):
        return None

    def get_profile(self, username):
        if not username or not username in aj.users.data['users']:
            return {}
        return aj.users.data['users'][username]

    def check_mail(self, mail):
        for user, details in aj.users.data['users'].items():
            email = details.get('email', None)
            if email == mail:
                return user
        return False

    def check_password_complexity(self,password):
        # TODO : add password policy
        return True

    def update_password(self, username, password):
        if username in aj.users.data['users']:
            hash = self.hash_password(password.encode('utf-8'))
            aj.users.data['users'][username]['password'] = hash
            aj.users.save()
            return True
        return False

    def signout(self):
        pass


@component(UserConfigProvider)
class UserAuthConfig(UserConfigProvider):
    id = 'users'
    name = 'Custom users'

    def __init__(self, context):
        UserConfigProvider.__init__(self, context)
        os_user = pwd.getpwuid(os.getuid())[0]
        try:
            username = context.identity
        except AttributeError:
            username = None
        _dir = os.path.expanduser(f'~{os_user}/.config/ajenti_auth_users')
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        self.path = os.path.join(_dir, f'userconfig_{username}.yml')
        if os.path.exists(self.path):
            self.load()
        else:
            self.data = {}

    def load(self):
        self.data = yaml.load(open(self.path), Loader=yaml.SafeLoader)

    def harden(self):
        os.chmod(self.path, stat.S_IRWXU)

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.safe_dump(
                self.data, default_flow_style=False, encoding='utf-8', allow_unicode=True
            ).decode('utf-8'))
        self.harden()