from ajenti.ui import *
from ajenti.api import * 

import dyndnsconfig

class DyndnsPlugin(CategoryPlugin):
    text = 'DynDns'
    icon = '/dl/dyndns/icon.png'
    folder = 'system'

    def on_init(self):
        self.conf = dyndnsconfig.Config(self.app)
        self.dyn = self.conf.read()

    def get_ui(self):
        ui = self.app.inflate('dyndns:main')
        td = ui.find('list')
	
        for entry in self.dyn:
            td.append(UI.DTR(
                UI.Label(text=entry.field),
                UI.Label(text=entry.value),
                UI.HContainer(
                    UI.TipIcon(icon='/dl/core/ui/stock/edit.png', text='Edit', id='edit/'+str(self.dyn.index(entry))),
                    UI.TipIcon(icon='/dl/core/ui/stock/delete.png', text='Remove', id='del/'+str(self.dyn.index(entry)))
                    ),
                ))    
	    
        if self._edit != None:
            ed = self.dyn[self._edit]    
            field = ui.find(ed.field)
            field.set('value', ed.field)
            field.set('selected', True)
            ui.find('value').set('value', ed.value)

        if self._display_dialog != True:
            ui.remove('dialog')

        return ui

    @event('button/click')
    def on_click(self, event, params, vars):
        self._display_dialog = False
        self._edit = None
        if(params[0] == 'add'):
            self._display_dialog = True       
        if(params[0] == 'del'):
            self.dyn.pop(int(params[1]))
            self.conf.save(self.dyn)
        if(params[0] == 'edit'):
            self._edit = int(params[1])
            self._display_dialog = True       
		   
    @event('dialog/submit')
    def on_submit(self, event, params, vars = None):
        self._display_dialog = False
        if params[0] == 'dialog':
            if vars.getvalue('action', '') == 'Cancel':
                self.put_message('info', 'Edit canceled.')
                return

            for entry in self.dyn:
                if(entry.field == vars.getvalue('field', '') and self._edit == None ):
                    self.put_message('error', 'Field '+entry.field+' already exist, edit it.')
                    return

            if(self._edit != None):
                self.dyn.pop(self._edit)
	   
            dyndns = dyndnsconfig.DynDnsProperty()
            dyndns.value = vars.getvalue('value', '')
            dyndns.field = vars.getvalue('field', 'username')
            self.dyn.append(dyndns)

            if vars.getvalue('action', '') == 'OK':
                self.conf.save(self.dyn)
