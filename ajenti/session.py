import log
import ui
import plugin

List = {}

def ProcessRequest(addr, req, h):
	global List

	if not List.has_key(addr):
		List[addr] = Session()
		List[addr].Client = addr
		List[addr].Init()

	List[addr].Process(req, h)



class Session:
	Client = ''
	UI = None
	Core = None
	Plugins = []

	def Init(self):
		log.info('Session', 'New session for ' + self.Client)
		self.Plugins = plugin.Instantiate()
		self.UI = ui.UI()

		self.Core = self.Plugins[0]
		for p in self.Plugins:
			p.OnLoad(self)
		for p in self.Plugins:
			p.OnPostLoad()
		for p in self.Plugins:
			p.Update()

		return


	def Process(self, req, h):
		#log.info('Session', 'Request from ' + self.Client + ' : ' + req)
		s = req.split(';')
		if s[0] == '/dl':
			self.ProcessDownload(s, h)
		if s[0] == '/handle':
			self.ProcessAjax(s, h)
		if s[0] == '/':
			h.wfile.write(self.UI.DumpBasePage())


	def ProcessDownload(self, s, h):
		try:
			f = './'
			if s[1]=='core': f += 'htdocs/'
			if s[1][0:4]=='plug': f += 'plugins/' + s[1][5:] + '/'
			f += s[2]
			fl = open(f)
			h.wfile.write(fl.read())
			fl.close()
		except:
			log.err('HTTP', '404: ' + f)
			pass

	def ProcessAjax(self, s, h):
		self.UI.Root.Handle(s[1], s[2], s[3])
		for p in self.Plugins:
			p.Update()
		self.SendUIUpdate(h)

	def SendUIUpdate(self, h):
		h.wfile.write(self.UI.DumpHTML())



	def RegisterPanel(self, p):
		self.Core.Switch.AddElement(p)

