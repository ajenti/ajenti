from ajenti.api import *
from ajenti import apis

import time


class PackageManagerComponent (Component):
    name = 'pkgman'
    
    def on_starting(self):
        self.status = apis.pkgman.Status()
        self.last_refresh = 0
        
        self.mgr = self.app.get_backend(apis.pkgman.IPackageManager)
            
    def get_status(self):
        if time.time() - self.last_refresh >= 5 * 60:
            self.last_refresh = time.time()
            self.mgr.refresh(self.status) 
        return self.status
        
    def refresh(self):
        self.last_refresh = 0
        return self.proxy.get_status()
        
    def run(self):
        while True:
            self.get_status()
            time.sleep(5*60 + 1)
            
    def __getattr__(self, attr):
        return getattr(self.mgr, attr)
        
