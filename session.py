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
	Coreplug = None 
	Plugins = []
	
	def Init(self):
		self.Plugins = plugin.Instantiate()
		log.info('Session', 'New session for ' + self.Client)
		self.UI = ui.UI()
		
		self.Coreplug = self.Plugins[0]
		self.Coreplug.OnLoad(self, self.UI)
		
		
		
	def Process(self, req, h):
		log.info('Session', 'Request from ' + self.Client + ' : ' + req)
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
			f += s[2]
			fl = open(f)
			h.wfile.write(fl.read())
			fl.close()
		except:
			pass

	def ProcessAjax(self, s, h):
		self.UI.Root.Handle(s[1], s[2], s[3])
		self.SendUIUpdate(h)

	def SendUIUpdate(self, h):
		#h.wfile.write('<xml><info>ui</info><data>' + self.UI.DumpHTML() + '</data></xml>')
		h.wfile.write(self.UI.DumpHTML())
	
	

		
