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
class ADSyncClassConfigEditor (ClassConfigEditor):
    title = _('Active Directory Syncronization')
    icon = 'refresh'

    def init(self):
        self.append(self.ui.inflate('configurator:ad-sync-config'))


@plugin
class ActiveDirectorySyncProvider (UserSyncProvider, BasePlugin):
    id = 'ad'
    title = 'Active Directory'
    default_classconfig = {
        'address': 'localhost',
        'domain': 'DOMAIN',
        'user': 'Administrator',
        'password': '',
        'base': 'cn=Users,dc=DOMAIN',
        'group': '',
    }
    classconfig_root = True
    classconfig_editor = ADSyncClassConfigEditor

    @classmethod
    def verify(cls):
        return ldap is not None

    def __get_ldap(self):
        if not ldap:
            return None

        c = ldap.initialize('ldap://' + self.classconfig['address'])
        c.bind_s('%s\\%s' % (self.classconfig['domain'], self.classconfig.get('user', 'Administrator')), self.classconfig['password'])
        c.set_option(ldap.OPT_REFERRALS, 0)
        return c

    def test(self):
        self.__search()

    def check_password(self, username, password):
        l = self.__get_ldap()
        try:
            return bool(l.bind_s('%s\\%s' % (self.classconfig['domain'], username), password))
        except Exception as e:
            print(e)
            return False

    def __search(self):
        l = self.__get_ldap()
        flt = '(|(objectClass=user)(objectClass=simpleSecurityObject))' 
        if self.classconfig.get('group', ''):
            flt = '(&%s(memberOf=%s))' % (flt, self.clasconfig['group'])
        return l.search_s(
            self.classconfig['base'],
            ldap.SCOPE_SUBTREE,
            flt,
            ['sAMAccountName']
        )

    def sync(self):
        found_names = []
        users = self.__search()
        for u in users:
            username = u[1]['sAMAccountName'][0]
            found_names.append(username)
            if not username in ajenti.config.tree.users:
                u = UserData()
                u.name = username
                ajenti.config.tree.users[username] = u

        for user in list(ajenti.config.tree.users.values()):
            if not user.name in found_names and user.name != 'root':
                ajenti.config.tree.users.pop(user.name)

        ajenti.config.save()
