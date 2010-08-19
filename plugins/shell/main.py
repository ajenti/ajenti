from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import shell, enquote	


class ShellPlugin(CategoryPlugin):
    text = 'Shell'
    icon = '/dl/shell/icon_small.png'
    folder = 'tools'
            
    def on_session_start(self):
        self._log = ''
        self._recent = []
        
    def get_status(self):
        return shell('echo `logname`@`hostname`')
        
    def get_ui(self):
        panel = UI.PluginPanel(
                    UI.Label(text=self.get_status()), 
                    title='Command shell',
                    icon='/dl/shell/icon.png'
                )
        panel.appendChild(self.get_default_ui())        
        return panel

    def get_default_ui(self):
        recent = [UI.SelectOption(text=x, value=x) for x in self._recent]
        log = UI.CustomHTML(enquote(self._log))
        
        frm = UI.FormBox(
                UI.TextInput(name='cmd', size=30),
                id='frmRun', hideok=True, hidecancel=True
              )
        frmr = UI.FormBox(
                UI.Select(*recent, name='cmd'),
                id='frmRecent', hideok=True, hidecancel=True
              )
        
        logc = UI.ScrollContainer(log, width=500, height=300)
        lt = UI.LayoutTable(
                UI.LayoutTableRow(frm, UI.Spacer(width=40), frmr),
                UI.LayoutTableRow(
                    UI.Button(text='Run', form='frmRun', onclick='form'),
                    UI.Spacer(width=40),
                    UI.Button(text='Repeat', form='frmRecent', onclick='form')
                )
             )
        t = UI.VContainer(lt, logc)
        return t
    
    def go(self, cmd):
        self._log = shell(cmd)
        rcnt = [cmd]
        if len(self._recent) > 0:
            for x in self._recent:
                rcnt.append(x)
        if len(rcnt) > 5:
            rcnt = rcnt[:5]
        self._recent = rcnt
                   
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'btnClear':
            self._log = ''
                
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        self.go(vars.getvalue('cmd', ''))

        
class ShellContent(ModuleContent):
    module = 'shell'
    path = __file__
    
    
