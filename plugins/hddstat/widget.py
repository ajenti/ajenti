from ajenti.ui import *
from ajenti import apis
from ajenti.com import implements, Plugin
from ajenti.api import *
from ajenti.utils import *
from ajenti import apis
from usage import UsageMeter

class StatWidget(Plugin):
	implements(apis.dashboard.IWidget)
	title = 'HDD Capacity'
	icon = '/dl/hddstat/icon.png'
	name = 'Capacity'
	style = 'normal'

	def get_ui(self, cfg, id=None):
		m = UsageMeter(self.app).prepare(cfg)
		#return UI.Label(text=str(m.get_value())+'%')
		#return UI.ProgressBar(value=m.get_value(), max=m.get_max(), width=220)
		return UI.HContainer(
			UI.ProgressBar(value=m.get_value(), max=m.get_max(), width=220),
			UI.Label(text=str(m.get_value())+'%'),
		)

	def handle(self, event, params, cfg, vars=None):
		pass

	def get_config_dialog(self):
		return None
	
	def process_config(self, vars):
		pass
