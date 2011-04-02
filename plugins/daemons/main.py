from ajenti.com import implements
from ajenti.api import *
from ajenti.ui import *
from backend import *

class DaemonsPlugin(CategoryPlugin):
    text = 'Daemons'
    icon = '/dl/daemons/icon.png'
    folder = 'apps'

    def on_init(self):
        self.mgr = Daemons(self.app)
        
    def on_session_start(self):
        self._editing = None
        
    def get_ui(self):
        ui = self.app.inflate('daemons:main')
        ts = ui.find('list')

        lst = self.mgr.list_all()
        for svc in lst:
            running = svc.running
            fn = '/dl/core/ui/stock/status-' + ('running.png' if svc.running else 'stopped.png')
            row = UI.DataTableRow(
                    UI.Image(file=fn),
                    UI.Label(text=svc.name),
                    UI.DataTableCell(
                        UI.MiniButton(text='Start', id='start/' + svc.name)
                            if not running else None,
                        UI.MiniButton(text='Stop', id='stop/' + svc.name) 
                            if running else None,
                        UI.MiniButton(text='Restart', id='restart/' + svc.name)
                            if running else None,
                        UI.MiniButton(text='Edit', id='edit/' + svc.name),
                        hidden=True
                    )
                  )
            ts.append(row)
            
        if self._editing != None:
            dlg = self.app.inflate('daemons:edit')
            ui.append('main', dlg)
            
        return ui

    @event('minibutton/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'start':
            self.mgr.start(params[1])
        if params[0] == 'restart':
            self.mgr.restart(params[1])
        if params[0] == 'stop':
            self.mgr.stop(params[1])
        if params[0] == 'edit':
            self._editing = params[1]

    @event('dialog/submit')
    def on_submit(self, event, params, vars):
        if params[0] == 'dlgEdit':
            self._editing = None
            
