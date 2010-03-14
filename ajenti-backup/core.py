import commands
import subprocess
import time
import os
import shlex

Jobs = {}

def RunJob(s):
	try:
		global Jobs
		Init()
		Jobs[s].Run()
	except:
		print 'Failed'
	return

def Commit():
	global Jobs

	Init()

	f = open('/etc/cron.d/ajenti-backup', 'w')
	f.write('SHELL=/bin/sh\n')
	for j in Jobs:
		if j.Time != '':
			f.write(Jobs[j].CronLine() + '\n')
	f.close()

	return 'Done'

def CancelJob(s):
	Init()
	ss = os.listdir('/var/run/ajenti-backup')
	if s + '.pid' in ss:
		commands.getstatusoutput('bash -c \'kill `cat /var/run/ajenti-backup/' + s + '.pid`\'')
	commands.getstatusoutput('bash -c \'rm /var/run/ajenti-backup/' + s + '.*\'')
	return

def Status():
	Init()
	s = os.listdir('/var/run/ajenti-backup/')
	for l in s:
		if '.pid' in l:
			print l.split('.')[0]
	return ''

def List():
	Init()
	global Jobs

	for j in Jobs:
		Jobs[j].Dump()
	return ''

def Init():
	global Jobs
	Jobs = {}

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
			l += e.Parse(ss)
			if e.Name != '':
				Jobs[e.Name] = e
	except:
		print 'Error in config file at job beginning at line', l, '\nAborting.'
	return

def Save():
	global Jobs

	try:
		f = open('/etc/ajenti/ajenti-backup.conf', 'w')
		for k in Jobs:
			Jobs[k].Save(f)
		f.close()
	except:
		pass

	Commit()
	return


class Job:
	Name = 'backup'
	Path = '~'
	Method = 'tar'
	SendBy = 'none'
	SendTo = ''
	Before = ''
	After = ''
	Temp = '/tmp'
	Exclude = None
	File = ''
	Time = '12 0 * * *'
	User = 'root'

	def __init__(self):
		self.Exclude = []

	def Parse(self, ss):
		ln = 1

		self.Name = ss[0].strip('[]')
		ss.remove(ss[0])
		while len(ss)>1 and (len(ss[0])==0 or not ss[0][0]=='['):
			if not (len(ss[0])==0 or ss[0][0] == '#'):
				l = ss[0].split('=')[0].strip(' \t')
				r = ss[0].split('=')[1].strip(' \t')
				if l == 'path':
					self.Path = r
				elif l == 'method':
					self.Method = r
				elif l == 'sendby':
					self.SendBy = r
				elif l == 'sendto':
					self.SendTo = r
				elif l == 'before':
					self.Before = r
				elif l == 'after':
					self.After = r
				elif l == 'temp':
					self.Temp = r
				elif l == 'time':
					self.Time = r
				elif l == 'user':
					self.User = r
				elif l == 'exclude':
					self.Exclude = r.split(':')
				elif l == 'file':
					self.File = r

			ss.remove(ss[0])
			ln += 1

		return ln

	def Dump(self):
		print 'Job \'' + self.Name + '\':'
		print 'Backup ' + self.Path + ' as ' + self.File + ' using \'' + self.Method + '\'.'
		print 'Temp dir:', self.Temp
		print 'Exclude:', self.Exclude
		print 'Send to ' + self.SendTo + ' using ' + self.SendBy
		if self.Before != '': print 'Run before: ' + self.Before
		if self.After != '': print 'Run after: ' + self.After
		print ''

	def Run(self):
		try:
			print 'Running job', self.Name
			if self.Before != '':
				print commands.getstatusoutput(self.Before)[1]

			pipe = None
			if self.Method == 'tar':
				cl = 'tar -cpvzf ' + self.Temp + '/'
				cl += self.File.replace('$d', '`date +%y_%m_%d`')
				cl += ' ' + self.Path + ' '
				for p in self.Exclude:
					if p != '' and p != ' ':
						cl += '--exclude=' + p + ' '
				print 'Running:', cl,
				a = shlex.split('bash -c \'' + cl + '\'')
				pipe = subprocess.Popen(a, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				commands.getstatusoutput('mkdir /var/run/ajenti-backup')
				commands.getstatusoutput('bash -c \'echo ' + str(pipe.pid) + ' > /var/run/ajenti-backup/' + self.Name + '.pid\'')
				while pipe.returncode == None:
					try:
						pipe.poll()
						s = pipe.stdout.readline().strip('\n')
						commands.getstatusoutput('bash -c \'echo ' + s + ' > /var/run/ajenti-backup/' + self.Name + '.status\' > /dev/null 2>&1')
					except:
						pass
			elif self.Method == 'none':
				pass
			else:
				print 'Invalid method!'

			print 'Backup built'

			if self.SendBy == 'copy':
				cl = 'cp -f ' + self.Temp + '/'
				cl += self.File.replace('$d', '`date +%y_%m_%d`')
				cl += ' ' + self.SendTo + '/' + self.File.replace('$d', '`date +%y_%m_%d`')
				print 'Running:', cl,
				print commands.getstatusoutput('bash -c \'' + cl + '\'')[1]
			elif self.SendBy == 'none':
				pass
			else:
				print 'Invalid SendBy!'

			print 'Backup sent'

			cl = 'rm -f ' + self.Temp + '/' + self.File.replace('$d', '`date +%y_%m_%d`')
			print 'Running:', cl,
			print commands.getstatusoutput('bash -c \'' + cl + '\'')[1]

			if self.After != '':
				print commands.getstatusoutput(self.After)[1]
		except Exception as e:
			print e
			pass

		commands.getstatusoutput('bash -c \'rm /var/run/ajenti-backup/' + self.Name + '.*\'')
		return

	def CronLine(self):
		s = self.Time + ' ' + self.User + ' ajenti-backup run ' + self.Name
		return s

	def Save(self, f):
		s = '[' + self.Name + ']\n'
		if self.Path != '':
			s += 'path = ' + self.Path + '\n'
		if self.Method != '':
			s += 'method = ' + self.Method + '\n'
		if self.SendTo != '':
			s += 'sendto = ' + self.SendTo + '\n'
		if self.SendBy != '':
			s += 'sendby = ' + self.SendBy + '\n'
		print self.Exclude
		if self.Exclude != ['']:
			s += 'exclude = ' + ':'.join(self.Exclude) + '\n'
		if self.File != '':
			s += 'file = ' + self.File + '\n'
		if self.Temp != '':
			s += 'temp = ' + self.Temp + '\n'
		if self.Before != '':
			s += 'before = ' + self.Before + '\n'
		if self.After != '':
			s += 'after = ' + self.After + '\n'
		if self.User != '':
			s += 'user = ' + self.User + '\n'
		if self.Time != '':
			s += 'time = ' + self.Time + '\n'
		f.write(s + '\n')

		return
