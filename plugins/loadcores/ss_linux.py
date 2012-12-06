from ajenti import apis
from ajenti.utils import shell
from ajenti.com import *

class LinuxSysStat(Plugin):
	implements(apis.loadcores.ILoadCores)
	platform = ['debian', 'arch', 'centos', 'fedora', 'gentoo']
	
	def get_loadcores(self):
		text = shell("mpstat -P ALL 1 1 | grep -v 'Linux' | grep -E -v '[0-9]{2}(\:[0-9]{2}){2}' | grep -v '^[[:space:]]*$' | grep -v 'CPU' | awk '{print 100-int($11)}'")
		
		loads = text.split()
		cores = len(loads)
		return (loads, cores)