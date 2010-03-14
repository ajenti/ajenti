ajenti_version = 'alpha (GIT snapshot)'
server_name = 'New server'
http_port = 8000

def load():
	global server_name, http_port

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
					server_name = v
				elif k == 'httpport':
					http_port = int(v)
					
			except:
				pass
	except:
		pass
