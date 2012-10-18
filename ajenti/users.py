import ajenti
from ajenti.api import *
from passlib.hash import sha512_crypt


def restrict(permission):
    def decorator(fx):
        def wrapper(*args, **kwargs):
            UserManager.get().require_permission(permission)
            return fx(*args, **kwargs)
        return wrapper
    return decorator


class SecurityError (Exception):
    def __init__(self, permission):
        self.permission = permission

    def __str__(self):
        return 'Permission "%s" required' % self.permission


@plugin
class UserManager (object):
    def check_password(self, username, password):
        if not username in ajenti.config.tree.users:
            return False
        type = 'plain'
        saved = ajenti.config.tree.users[username].password
        if '|' in saved:
            type, saved = saved.split('|')

        if type == 'plain':
            hash = password
            return hash == saved
        elif sha512_crypt.identify(saved):
            return sha512_crypt.verify(password, saved)

    def hash_password(self, password):
        if not password.startswith('sha512|'):
            password = 'sha512|%s' % sha512_crypt.encrypt(password)
        return password

    def require_permission(self, permission):
        context = extract_context()
        if context.user.name == 'root':
            return
        if not permission in context.user.permissions:
            raise SecurityError(permission)


@interface
class PermissionProvider (object):
    def get_permissions(self):
        return []

    def get_name(self):
        return ''
