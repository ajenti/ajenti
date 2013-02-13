from ajenti.api import *
from ajenti import apis


class LoadCoresMeter (LinearMeter):
	name = 'CPU Load cores'
	category = 'System'
	transform = 'fsize_percent'
	
	def init(self):
		self.cores = self.app.get_backend(apis.loadcores.ILoadCores).get_loadcores()
	
	def get_max(self):
		return 100
	