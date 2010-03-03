import commands
import log

def Script(p, s, a=''):
	log.info('Script', 'Executing ' + './plugins/' + p + '/scripts/' + s + ' ' + a)
	return commands.getstatusoutput('./plugins/' + p + '/scripts/' + s + ' ' + a)[1]

def Shell(s):
	return commands.getstatusoutput(s)[1]

def DetectDistro():
	s, r = commands.getstatusoutput('lsb_release -sd')
	if s == 0: return r
	s, r = commands.getstatusoutput('uname -mrs')
	return r
