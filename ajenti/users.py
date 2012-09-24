import ajenti
from ajenti.api import *
from passlib.hash import sha512_crypt


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
        if type == 'sha512':
            hash = sha512_crypt.encrypt(passw)

        return hash == saved
