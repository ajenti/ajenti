from passlib.hash import sha512_crypt

import ajenti
import ajenti.usersync
from ajenti.api import *


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
class UserManager (BasePlugin):
    default_classconfig = {'sync-provider': ''}
    classconfig_root = True

    def check_password(self, username, password):
        """
        Verifies the given username/password combo
        """
        provider = self.get_sync_provider(fallback=True)
        provider.sync()
        return provider.check_password(username, password)

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

    def get_sync_provider(self, fallback=False):
        for p in ajenti.usersync.UserSyncProvider.get_classes():
            p.get()
            if p.id == self.classconfig['sync-provider']:
                if not p.get().test() and fallback:
                    return ajenti.usersync.AjentiSyncProvider.get()
                return p.get()

    def set_sync_provider(self, provider_id):
        self.classconfig['sync-provider'] = provider_id
        self.save_classconfig()


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
