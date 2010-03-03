import commands
import log

def Script(p, s, a=''):
	log.info('Script', 'Executing ' + './plugins/' + p + '/scripts/' + s + ' ' + a)
	return commands.getstatusoutput('./plugins/' + p + '/scripts/' + s + ' ' + a)[1]
