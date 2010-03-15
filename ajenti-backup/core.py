import commands
import subprocess
import time
import os
import shlex

jobs = {}

def run_job(s):
	try:
		global jobs
		init()
		jobs[s].run()
	except:
		print 'Failed'
	return

def commit():
	global jobs

	init()

	f = open('/etc/cron.d/ajenti-backup', 'w')
	f.write('SHELL=/bin/sh\n')
	for j in jobs:
		if jobs[j].time != '':
			f.write(jobs[j].cronline() + '\n')
	f.close()

	return 'Done'

def cancel_job(s):
	init()
	ss = os.listdir('/var/run/ajenti-backup')
	if s + '.pid' in ss:
		commands.getstatusoutput('bash -c \'kill `cat /var/run/ajenti-backup/' + s + '.pid`\'')
	commands.getstatusoutput('bash -c \'rm /var/run/ajenti-backup/' + s + '.*\'')
	return

def status():
	init()
	s = os.listdir('/var/run/ajenti-backup/')
	for l in s:
		if '.pid' in l:
			print l.split('.')[0]
	return ''

def list():
	init()
	global jobs

	for j in jobs:
		jobs[j].Dump()
	return ''

def init():
	global jobs
	jobs = {}

	try:
		f = open('/etc/ajenti/ajenti-backup.conf', 'r')
		ss = f.read().splitlines()
		for s in ss:
			s.strip(' \t\n\r')
		f.close()
	except:
		pass

	l = 0
	try:
		while len(ss)>1:
			while len(ss[0])>1 and not ss[0][0]=='[':
				ss = ss[1:]
				l += 1
			if len(ss)==1: return
			e = Job()
			l += e.parse(ss)
			if e.name != '':
				jobs[e.name] = e
	except:
		print 'Error in config file at job beginning at line', l, '\nAborting.'
	return

def save():
	global jobs

	try:
		f = open('/etc/ajenti/ajenti-backup.conf', 'w')
		for k in jobs:
			jobs[k].save(f)
		f.close()
	except:
		pass

	commit()
	return


class Job:
	name = 'backup'
	path = '~'
	method = 'tar'
	sendby = 'none'
	sendto = ''
	before = ''
	after = ''
	temp = '/tmp'
	exclude = None
	file = ''
	time = '12 0 * * *'
	user = 'root'

	def __init__(self):
		self.exclude = []

	def parse(self, ss):
		ln = 1

		self.name = ss[0].strip('[]')
		ss.remove(ss[0])
		while len(ss)>1 and (len(ss[0])==0 or not ss[0][0]=='['):
			if not (len(ss[0])==0 or ss[0][0] == '#'):
				l = ss[0].split('=')[0].strip(' \t')
				r = ss[0].split('=')[1].strip(' \t')
				if l == 'path':
					self.path = r
				elif l == 'method':
					self.method = r
				elif l == 'sendby':
					self.sendby = r
				elif l == 'sendto':
					self.sendto = r
				elif l == 'before':
					self.before = r
				elif l == 'after':
					self.after = r
				elif l == 'temp':
					self.temp = r
				elif l == 'time':
					self.time = r
				elif l == 'user':
					self.user = r
				elif l == 'exclude':
					self.exclude = r.split(':')
				elif l == 'file':
					self.file = r

			ss.remove(ss[0])
			ln += 1

		return ln

	def dump(self):
		print 'job \'' + self.name + '\':'
		print 'Backup ' + self.path + ' as ' + self.file + ' using \'' + self.method + '\'.'
		print 'temp dir:', self.temp
		print 'exclude:', self.exclude
		print 'Send to ' + self.sendto + ' using ' + self.sendby
		if self.before != '': print 'Run before: ' + self.before
		if self.after != '': print 'Run after: ' + self.after
		print ''

	def run(self):
		try:
			print 'Running job', self.name
			if self.before != '':
				print commands.getstatusoutput(self.before)[1]

			pipe = None
			if self.method == 'tar':
				cl = 'tar -cpvzf ' + self.temp + '/'
				cl += self.file.replace('$d', '`date +%y_%m_%d`')
				cl += ' ' + self.path + ' '
				for p in self.exclude:
					if p != '' and p != ' ':
						cl += '--exclude=' + p + ' '
				print 'Running:', cl,
				a = shlex.split('bash -c \'' + cl + '\'')
				pipe = subprocess.Popen(a, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				commands.getstatusoutput('mkdir /var/run/ajenti-backup')
				commands.getstatusoutput('bash -c \'echo ' + str(pipe.pid) + ' > /var/run/ajenti-backup/' + self.name + '.pid\'')
				while pipe.returncode == None:
					try:
						pipe.poll()
						s = pipe.stdout.readline().strip('\n')
						commands.getstatusoutput('bash -c \'echo ' + s + ' > /var/run/ajenti-backup/' + self.name + '.status\' > /dev/null 2>&1')
					except:
						pass
			elif self.method == 'none':
				pass
			else:
				print 'Invalid method!'

			print 'Backup built'

			if self.sendby == 'copy':
				cl = 'cp -f ' + self.temp + '/'
				cl += self.file.replace('$d', '`date +%y_%m_%d`')
				cl += ' ' + self.sendto + '/' + self.file.replace('$d', '`date +%y_%m_%d`')
				print 'Running:', cl,
				print commands.getstatusoutput('bash -c \'' + cl + '\'')[1]
			elif self.sendby == 'none':
				pass
			else:
				print 'Invalid sendby!'

			print 'Backup sent'

			cl = 'rm -f ' + self.temp + '/' + self.file.replace('$d', '`date +%y_%m_%d`')
			print 'Running:', cl,
			print commands.getstatusoutput('bash -c \'' + cl + '\'')[1]

			if self.after != '':
				print commands.getstatusoutput(self.after)[1]
		except Exception as e:
			print e
			pass

		commands.getstatusoutput('bash -c \'rm /var/run/ajenti-backup/' + self.name + '.*\'')
		return

	def cronline(self):
		s = self.time + ' ' + self.user + ' ajenti-backup run ' + self.name
		return s

	def save(self, f):
		s = '[' + self.name + ']\n'
		if self.path != '':
			s += 'path = ' + self.path + '\n'
		if self.method != '':
			s += 'method = ' + self.method + '\n'
		if self.sendto != '':
			s += 'sendto = ' + self.sendto + '\n'
		if self.sendby != '':
			s += 'sendby = ' + self.sendby + '\n'
		print self.exclude
		if self.exclude != ['']:
			s += 'exclude = ' + ':'.join(self.exclude) + '\n'
		if self.file != '':
			s += 'file = ' + self.file + '\n'
		if self.temp != '':
			s += 'temp = ' + self.temp + '\n'
		if self.before != '':
			s += 'before = ' + self.before + '\n'
		if self.after != '':
			s += 'after = ' + self.after + '\n'
		if self.user != '':
			s += 'user = ' + self.user + '\n'
		if self.time != '':
			s += 'time = ' + self.time + '\n'
		f.write(s + '\n')

		return
