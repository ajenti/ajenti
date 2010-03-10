Actions = {}

def RegisterAction(a):
	global Actions
	n = a.Plugin + '/' + a.Name
	Actions[n] = a

class Action(object):
	Name = ''
	Plugin = ''

	def Run(self, params = None):
		pass