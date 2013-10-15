from passlib.hash import sha512_crypt

import ajenti
from ajenti.api import *

from base import UserSyncProvider


@plugin
class AjentiSyncProvider (UserSyncProvider):
    id = ''
    title = _('Off')
    
    def test(self):
        return True

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

    def sync(self):
        pass