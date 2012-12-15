from ajenti.api import *
from ajenti.utils import shell

class Cpu(LinearMeter):
    name = 'CPU usage'
    category = 'System'
    transform = 'percent'
    
    def get_usage(self):
         if detect_platform() == 'freebsd':
             u = shell('ps h -xeo pcpu').split()
         else:
             u = shell('ps h -eo pcpu').split()
         b=0.0
         for a in u:
            try:
                b += float(a)
            except:
                pass
         if detect_platform() == 'freebsd':
             ncpus = shell('sysctl -n kern.smp.cpus')
             if not ncpus.split()[0].isdigit():
                 ncpus = 1
             if ncpus == '0' or ncpus < 0:
                 ncpus = 1
             b = b/float(ncpus)
         return b
    
    def get_value(self):
        return self.get_usage()
    
    def get_min(self):
        return 0
    
    def get_max(self):
        return 100
