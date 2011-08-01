from ajenti.ui import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin
from ajenti.api import *

from client import SVClient


class SVWidget(Plugin):
    implements(IDashboardWidget)
    icon = '/dl/supervisor/icon.png'
    name = 'Supervisor process'
    title = None
    style = 'linear'

    def __init__(self):
        self.iface = None

    def get_ui(self, cfg, id=None):
        mgr = SVClient(self.app)
        running = False

        for x in mgr.status():
            if x['name'] == cfg and x['status'] == 'RUNNING':
                running = True

        self.title = cfg
        self.icon = '/dl/core/ui/stock/service-' + ('run.png' if running else 'stop.png')

        ui = self.app.inflate('supervisor:widget')
        if running:
            ui.remove('start')
            ui.find('stop').set('id', id+'/stop')
            ui.find('restart').set('id', id+'/restart')
        else:
            ui.remove('stop')
            ui.remove('restart')
            ui.find('start').set('id', id+'/start')
        return ui

    def handle(self, event, params, cfg, vars=None):
        mgr = SVClient(self.app)
        if params[0] == 'start':
            mgr.start(cfg)
        if params[0] == 'stop':
            mgr.stop(cfg)
        if params[0] == 'restart':
            mgr.restart(cfg)

    def get_config_dialog(self):
        mgr = SVClient(self.app)
        dlg = self.app.inflate('supervisor:widget-config')
        for s in mgr.status():
            dlg.append('list', UI.SelectOption(
                value=s['name'],
                text=s['name'],
            ))
        return dlg

    def process_config(self, vars):
        return vars.getvalue('svc', None)
