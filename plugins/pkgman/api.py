from ajenti.com import *
from ajenti.app.api import *

class IPackageManager(Interface):
    def refresh(self, st):
        pass

    def get_lists(self, st):
        pass

    def search(self, q):
        pass

    def mark_install(self, st, name):
        pass

    def mark_remove(self, st, name):
        pass

    def mark_cancel(self, st, name):
        pass

    def apply(self, st):
        pass

    def is_busy(self):
        pass

    def get_busy_status(self):
        pass

    def get_expected_result(self, st):
        pass


class Package(object):
    name = ''
    version = ''
    state = ''
    action = ''


class Status(object):
    upgradeable = None
    pending = None
    fulllist = None
