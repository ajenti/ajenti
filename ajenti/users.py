import logging
import syslog
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
@persistent
class UserManager (BasePlugin):
    default_classconfig = {'sync-provider': ''}
    classconfig_root = True

    def check_password(self, username, password):
        """
        Verifies the given username/password combo

        :type username: str
        :type password: str
        :rtype: bool
        """
        provider = self.get_sync_provider(fallback=True)
        if username == 'root' and not provider.syncs_root:
            provider = ajenti.usersync.AjentiSyncProvider.get()

        if not username in ajenti.config.tree.users:
            return False
            
        try:
            provider.sync()
        except Exception as e:
            logging.error(str(e))

        result = provider.check_password(username, password)

        provider_name = type(provider).__name__
        if not result:
            msg = 'failed login attempt for %s ("%s") through %s' % (username, password, provider_name)
            syslog.syslog(syslog.LOG_WARNING, msg)
            logging.warn(msg)
        else:
            msg = 'user %s logged in through %s' % (username, provider_name)
            syslog.syslog(syslog.LOG_INFO, msg)
            logging.info(msg)
        return result

    def hash_password(self, password):
        """
        :type password: str
        :rtype: str
        """
        if not password.startswith('sha512|'):
            password = 'sha512|%s' % sha512_crypt.encrypt(password)
        return password

    def has_permission(self, permission):
        """
        Checks whether the current user has a permission
        
        :type permission: str
        :rtype: bool
        """
        context = extract_context()
        if context.user.name == 'root':
            return True
        if not permission in context.user.permissions:
            return False
        return True

    def require_permission(self, permission):
        """
        Checks current user for given permission and raises :class:`SecurityError` if he doesn't have one
        :type permission: str
        :raises: SecurityError
        """
        if not self.has_permission(permission):
            raise SecurityError(permission)

        
    def get_sync_provider(self, fallback=False):
        """
        :type fallback: bool
        :rtype: ajenti.usersync.UserSyncProvider
        """
        for p in ajenti.usersync.UserSyncProvider.get_classes():
            p.get()
            if p.id == self.classconfig['sync-provider']:
                try:
                    p.get().test()
                except:
                    if fallback:
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
        """ 
        Should return a list of permission names 

        :rtype: list
        """
        return []

    def get_name(self):
        """
        Should return a human-friendly name for this set of permissions (displayed in Configurator) 
        :rtype: str
        """
        return ''


__all__ = ['restrict', 'PermissionProvider', 'SecurityError', 'UserManager']
