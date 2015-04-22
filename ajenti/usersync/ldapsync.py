try:
    import ldap
except ImportError:
    ldap = None

import ajenti
from ajenti.api import *
from ajenti.plugins.configurator.api import ClassConfigEditor

from reconfigure.items.ajenti import UserData

from base import UserSyncProvider


@plugin
class LDAPSyncClassConfigEditor (ClassConfigEditor):
    title = _('LDAP User Syncronization')
    icon = 'refresh'

    def init(self):
        self.append(self.ui.inflate('configurator:ldap-sync-config'))


@plugin
class LDAPSyncProvider (UserSyncProvider):
    id = 'ldap'
    title = 'LDAP'
    default_classconfig = {
        'url': 'ldap://localhost',
        'admin_dn': 'cn=admin,dc=nodomain',
        'auth_dn': 'dc=nodomain',
        'secret': '',
    }
    classconfig_root = True
    classconfig_editor = LDAPSyncClassConfigEditor

    def __get_ldap(self):
        if not ldap:
            return None

        c = ldap.initialize(self.classconfig['url'])
        c.bind_s(self.classconfig['admin_dn'], self.classconfig['secret'])
        return c

    @classmethod
    def verify(cls):
        return ldap is not None

    def test(self):
        self.__get_ldap()

    def check_password(self, username, password):
        l = self.__get_ldap()
        try:
            return bool(l.bind_s('cn=%s,' % username + self.classconfig['auth_dn'], password))
        except Exception as e:
            print(e)
            return False

    def sync(self):
        found_names = []
        l = self.__get_ldap()
        users = l.search_s(
            self.classconfig['auth_dn'],
            ldap.SCOPE_SUBTREE,
            '(|(objectClass=user)(objectClass=simpleSecurityObject)(objectClass=inetOrgPerson))',
            ['cn']
        )
        for u in users:
            username = u[1]['cn'][0]
            found_names.append(username)
            if not username in ajenti.config.tree.users:
                u = UserData()
                u.name = username
                ajenti.config.tree.users[username] = u

        for user in list(ajenti.config.tree.users.values()):
            if not user.name in found_names and user.name != 'root':
                ajenti.config.tree.users.pop(user.name)

        ajenti.config.save()
