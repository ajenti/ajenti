import ajenti
from ajenti.api import *
from passlib.hash import sha512_crypt


def restrict(permission):
    """
    Marks a decorated function as requiring ``permission``. If the invoking user doesn't have one, :class:`SecurityError` is raised.
    """
    def decorator(fx):
        def wrapper(*args, **kwargs):
            UserManager.get().require_permission(permission)
            return fx(*args, **kwargs)
        return wrapper
    return decorator


class SecurityError (Exception):
    """
    Indicates that user didn't have a required permission.

    .. attribute:: permission

        permission ID
    """

    def __init__(self, permission):
        self.permission = permission

    def __str__(self):
        return 'Permission "%s" required' % self.permission


@plugin
class UserManager (object):
    def check_password(self, username, password):
        """
        Verifies the given username/password combo
        """

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
        """
        Checks current user for given permissing and raises :class:`SecurityError` if he doesn't have one
        """

        context = extract_context()
        if context.user.name == 'root':
            return
        if not permission in context.user.permissions:
            raise SecurityError(permission)


@interface
class PermissionProvider (object):
    """
    Override to create your own set of permissions
    """

    def get_permissions(self):
        """ Should return a list of permission names """
        return []

    def get_name(self):
        """ Should return a human-friendly name for this set of permissions (displayed in Configurator) """
        return ''


__all__ = ['restrict', 'PermissionProvider', 'SecurityError', 'UserManager']
