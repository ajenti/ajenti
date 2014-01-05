import ldap

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
    }
    classconfig_root = True
    classconfig_editor = ADSyncClassConfigEditor

    def __get_ldap(self):
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
        except Exception, e:
            print e
            return False

    def __search(self):
        l = self.__get_ldap()
        return l.search_s(
            self.classconfig['base'], 
            ldap.SCOPE_SUBTREE, 
            '(|(objectClass=user)(objectClass=simpleSecurityObject))', 
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
