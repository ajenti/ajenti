from ajenti.api import *
from ajenti.utils import shell

class DiskUsageMeter(LinearMeter):
    name = 'Disk usage'
    category = 'System'
    transform = 'percent'
   
    def get_usage(self, dev):
        u = shell('df --total | grep -w %s' % dev)
        if dev == 'total':
            u = int(u.split().pop().strip('%'))
        else:
            u = int(u.split().pop(-2).strip('%'))
        return u
    
    def get_value(self, dev):
        return self.get_usage(dev)
    
    def get_min(self):
        return 0
    
    def get_max(self):
        return 100


