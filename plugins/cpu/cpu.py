from ajenti.api import *
from ajenti.utils import shell

class Cpu(LinearMeter):
    name = 'CPU usage'
    category = 'System'
    transform = 'percent'
    
    def get_usage(self):
         u = shell('ps h -eo pcpu').split()
	 b=0.0
         for a in u:  
            b += float(a)
         return b
    
    def get_value(self):
        return self.get_usage()
    
    def get_min(self):
        return 0
    
    def get_max(self):
        return 100
