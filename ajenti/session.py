import log
import ui
import plugin
import tools
import util

List = {}

def ProcessRequest(addr, req, h):
	global List

	if not List.has_key(addr):
		List[addr] = Session()
		List[addr].Client = addr
		List[addr].Init()

	List[addr].Process(req, h)


def destroyAll():
	global List
	
	for s in List:
		List[s].destroy()
		
	
class Session:
	Client = ''
	UI = None
	Core = None
	Plugins = []
	Platform = 'generic'

	def Init(self):
		log.info('Session', 'New session for ' + self.Client)
		self.Plugins = plugin.Instantiate()
		self.UI = ui.UI()
		self.Core = self.Plugins[0]
		self.Platform = util.detect_platform()

		for p in self.Plugins:
			if not ('any' in p.Master.Platform or self.Platform in p.Master.Platform):
				self.Plugins.remove(p)
				log.warn('Plugins', 'Plugin ' + p.Name + ' doesn\'t support current platform \'' + self.Platform + '\'')

		for p in self.Plugins:
			p.OnLoad(self)
		for p in self.Plugins:
			p.OnPostLoad()
		for p in self.Plugins:
			p.Update()

		return


	def Process(self, req, h):
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

	def destroy(self):
		log.info('Session', 'Destroying session for ' + self.Client)
		for p in self.Plugins:
			p.destroy()
