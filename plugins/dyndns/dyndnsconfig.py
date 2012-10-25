import os

from ajenti.api import *
from ajenti.utils import *
from ajenti.com import *

class DynDns:
    def __init__(self):
	self.field = '';
	self.value = '';

class Config (Plugin):
    implements(IConfigurable)
    name = 'Dyndns Configuration'
    id = 'conf'
    pathfile = '/etc/inadyn.conf'

    def list_files(self):
    	return [self.pathfile]

    def read(self):
	isFileExist = os.path.isfile(self.pathfile)
	if(isFileExist == False):
	    f = open(self.pathfile,'w')
	    f.close()
	    return

	file = ConfManager.get().load('inadyn', self.pathfile).split('\n')
        c = []

	if file is not None:
	    for f in file:
		if f != '' :
		    try:
			s = f.split('\t')
			field, val = s
			d = DynDns()
			d.field = field
			d.value = val
			c.append(d)
		    except:
			pass
	return c

    def save(self, data):
        isFileExist = os.path.isfile(self.pathfile)
        if(isFileExist == False):
            f = open(self.pathfile,'w')
            f.close()
            
        dataRow = ''
        for aData in data:
            dataRow += '%s\t%s\n' % (aData.field, aData.value)
        ConfManager.get().save('inadyn', self.pathfile, dataRow)
	#ConfManager.get().commit('inadyn')
