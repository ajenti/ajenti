actions = {}

def register_action(a):
	global actions
	n = a.plugin + '/' + a.name
	actions[n] = a

class Action(object):
	name = ''
	plugin = ''

	def run(self, params=None):
		pass
		