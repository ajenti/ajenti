from ajenti.api import *
from ajenti.utils import shell

class UsageMeter(LinearMeter):
	name = 'Disk usage'
	category = 'System'
	transform = 'percent'
	
	def get_usage(self):
		u = int(shell('df --total | grep total').split().pop().strip('%'))
		print 'Usage: ', u
		return u
	
	def get_value(self):
		return self.get_usage()
	
	def get_min(self):
		return 0
	
	def get_max(self):
		return 100
