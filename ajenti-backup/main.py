import sys
import config
import core

def ShowHelp():
	print 'Ajenti Backup ' + config.AjentiVersion
	print 'The automatic backup system for Ajenti server administration kit'
	print """usage:
	ajenti-backup run <job>		Start a job
	ajenti-backup list			Show the saved jobs
	ajenti-backup status		Show running jobs
	ajenti-backup commit		Apply the config
	ajenti-backup cancel <job>	Cancel a running job
"""

if len(sys.argv) == 1:
	ShowHelp()
else:
	if sys.argv[1] == 'status':
		print core.Status()
	elif sys.argv[1] == 'list':
		print core.List()
	elif sys.argv[1] == 'commit':
		print core.Commit()
	elif sys.argv[1] == 'run':
		if len(sys.argv) == 2:
			ShowHelp()
		else:
			core.RunJob(sys.argv[2])
	elif sys.argv[1] == 'cancel':
		if len(sys.argv) == 2:
			ShowHelp()
		else:
			core.CancelJob(sys.argv[2])
	else:
		ShowHelp()

