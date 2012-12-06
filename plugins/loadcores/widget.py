from ajenti.ui import *
from ajenti import apis
from ajenti.com import implements, Plugin
from ajenti.api import *
from ajenti.utils import *

class CoresWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Load Cores'
    icon = '/dl/loadcores/widget.png'
    name = 'Load Cores'
    style = 'normal'

    def get_ui(self, cfg, id=None):
		ui = self.app.inflate('loadcores:main')
		stat = self.app.get_backend(apis.loadcores.ILoadCores)
		loads, cores = stat.get_loadcores()
		
		cpua = UI.HContainer(
			UI.Label(text='CPUA'),
			UI.ProgressBar(value=eval(loads[0]), max=100, width=220),
			UI.Label(text=str(loads[0])+'%')
		)

		ui.append('cores', UI.Div(id='cpua'));
		ui.append('cpua', cpua);
		
		i = 1
		while i < int(cores):
			core = UI.HContainer(
				UI.Label(text='CPU'+str(i)),
				UI.ProgressBar(value=eval(loads[i]), max=100, width=220),
				UI.Label(text=str(loads[i])+'%')
			)
			i = i + 1

			ui.append('cores', UI.Div(id='core'+str(i)));
			ui.append('core'+str(i), core);
			
		return ui

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None

    def process_config(self, vars):
        pass
		