import subprocess

import ajenti
from ajenti.api import *

from reconfigure.items.ajenti import UserData

from base import UserSyncProvider
from pam import authenticate



@plugin
class UNIXSyncProvider (UserSyncProvider):
    id = 'unix'
    title = _('OS users')

    def test(self):
        return True

    def check_password(self, username, password):
        return authenticate(username, password, 'passwd')

    def sync(self):
        found_names = []
        for l in subprocess.check_output(['passwd', '-Sa']).splitlines():
            l = l.split()
            if len(l) >= 2:
                username, state = l[:2]
                if 'P' in state:
                    found_names.append(username)
                    if not username in ajenti.config.tree.users:
                        u = UserData()
                        u.name = username
                        ajenti.config.tree.users[username] = u
        
        for user in list(ajenti.config.tree.users.values()):
            if not user.name in found_names and user.name != 'root':
                ajenti.config.tree.users.pop(user.name)

        ajenti.config.save()
