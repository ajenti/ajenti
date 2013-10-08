from ajenti.api import *


@interface
class UserSyncProvider (object):
    def test(self):
        return False

    def check_password(self, username, password):
        return False

    def sync(self):
        pass