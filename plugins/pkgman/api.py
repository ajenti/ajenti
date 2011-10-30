from ajenti.com import *
from ajenti.api import *
from ajenti.apis import API


class PkgMan(API):
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

        def mark_cancel_all(self, st):
            pass
    
        def apply(self, st):
            pass

        def is_busy(self):
            pass

        def get_busy_status(self):
            pass

        def get_expected_result(self, st):
            pass

        def abort(self):
            pass
            
        def get_info(self, pkg):
            pass

        def get_info_ui(self, pkg):
            pass
            
                        
    class Package(object):
        def __init__(self):
            self.name = ''
            self.version = ''
            self.state = ''
            self.description = ''


    class PackageInfo(object):
        def __init__(self):
            self.installed = ''
            self.available = ''
            self.description = ''            
    
    
    class Status(object):
        upgradeable = {}
        pending = {}}
        full = {}}
        
