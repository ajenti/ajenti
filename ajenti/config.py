# Configuration file

AjentiVersion = 'alpha (GIT snapshot)'
ServerName = 'New server'

# Http port
HttpPort = 8000

def Load():
	global ServerName, HttpPort

	try:
		f = open('/etc/ajenti/ajenti.conf')
		ss = f.read().splitlines()
		f.close()

		for s in ss:
			try:
				s = s.strip(' \t\r\n').split('=')
				k = s[0].strip(' \t')
				v = s[1].strip(' \t')
				if k == 'servername':
					ServerName = v
				elif k == 'httpport':
					HttpPort = int(v)
					
			except:
				pass
	except:
		pass
