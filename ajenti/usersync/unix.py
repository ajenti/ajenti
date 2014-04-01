import ajenti
from ajenti.api import *

from reconfigure.items.ajenti import UserData

from base import UserSyncProvider
from pam import authenticate



@plugin
class UNIXSyncProvider (UserSyncProvider):
    id = 'unix'
    title = _('OS users')
    syncs_root = True

    def test(self):
        pass

    def check_password(self, username, password):
        return authenticate(username, password, 'passwd')

    def sync(self):
        found_names = []
        for l in open('/etc/shadow').read().splitlines():
            l = l.split(':')
            if len(l) >= 2:
                username, pwd = l[:2]
                if len(pwd) > 2:
                    found_names.append(username)
                    if not username in ajenti.config.tree.users:
                        u = UserData()
                        u.name = username
                        ajenti.config.tree.users[username] = u

        for user in list(ajenti.config.tree.users.values()):
            if not user.name in found_names and user.name != 'root':
                ajenti.config.tree.users.pop(user.name)

        ajenti.config.save()
