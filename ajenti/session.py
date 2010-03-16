import log
import ui
import plugin
import tools
import util

list = {}

def process_request(addr, req, h):
	global list

	if not list.has_key(addr):
		list[addr] = Session()
		list[addr].client = addr
		list[addr].init()

	list[addr].process(req, h)


def destroy_all():
	global list

	for s in list:
		list[s].destroy()


class Session:
	client = ''
	ui = None
	core = None
	plugins = []
	platform = 'generic'

	def init(self):
		log.info('Session', 'New session for ' + self.client)
		self.plugins = plugin.instantiate()
		self.ui = ui.UI()
		self.core = self.plugins[0] # This needs to be done in some better way
		self.platform = util.detect_platform()

		for p in self.plugins:
			if not 'any' in p.master.platform and \
				not self.platform in p.master.platform:
				self.plugins.remove(p)
				log.warn('Plugins', 'Plugin ' + p.name + ' doesn\'t support current platform \'' + self.platform + '\'')

		for p in self.plugins:
			p._on_load(self)
		for p in self.plugins:
			p._on_post_load()
		for p in self.plugins:
			p.update()

		return

	def process(self, req, h):
		s = req.split(';')
		if s[0] == '/dl':
			self.process_download(s, h)
		if s[0] == '/handle':
			self.process_ajax(s, h)
		if s[0] == '/':
			h.wfile.write(self.ui.dump_base_page())

	def process_download(self, s, h):
		try:
			f = './'
			if s[1] == 'core':
				f += 'htdocs/'
			if s[1][0:4] == 'plug':
				f += 'plugins/' + s[1][5:] + '/'
			f += s[2]
			fl = open(f)
			h.wfile.write(fl.read())
			fl.close()
		except:
			log.err('HTTP', 'Error processing ' + f)
			pass

	def process_ajax(self, s, h):
		self.ui.root.handle(s[1], s[2], s[3])
		for p in self.plugins:
			p.update()
		self.send_ui_update(h)

	def send_ui_update(self, h):
		h.wfile.write(self.ui.dump_HTML())

	def register_panel(self, p):
		p.visible = False
		self.core.switch.add_element(p)

	def schedule_update(self, t):
		self.ui.update_timer = t

	def destroy(self):
		log.info('Session', 'Destroying session for ' + self.client)
		for p in self.plugins:
			p.destroy()
