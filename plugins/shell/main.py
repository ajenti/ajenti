from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import shell, enquote, BackgroundProcess
from ajenti.plugins.core.api import *


class ShellPlugin(CategoryPlugin):
    text = 'Shell'
    icon = '/dl/shell/icon.png'
    folder = 'tools'

    def on_session_start(self):
        self._recent = []
        self._process = BackgroundProcess('')

    def get_status(self):
        return shell('echo `logname`@`hostname`')

    def get_ui(self):
        panel = UI.PluginPanel(
                    UI.Label(text=self.get_status()),
                    title='Command shell',
                    icon='/dl/shell/icon.png'
                )
        panel.append(self.get_default_ui())
        return panel

    def get_default_ui(self):
        recent = [UI.SelectOption(text=x[0:40] + '...' if len(x) > 40 else x,
                                  value=x) for x in self._recent]
        log = UI.CustomHTML(html=enquote(self._process.output + self._process.errors))

        frm = UI.FormBox(
                UI.TextInput(name='cmd', size=30, id='shell-command'),
                id='frmRun', hideok=True, hidecancel=True
              )
        frmr = UI.FormBox(
                UI.Select(*recent, name='cmd', id='shell-recent',
                          onchange='shellRecentClick()',
                          onmousedown='shellRecentClick()'),
                id='frmRecent', hideok=True, hidecancel=True
              )

        logc = UI.ScrollContainer(log, width=500, height=300)
        lt = UI.VContainer(
                UI.HContainer(
                    frm, 
                    UI.Button(text='Run', form='frmRun', onclick='form')), 
                UI.HContainer(
                    UI.Label(text='Repeat:'),
                    frmr
                )
             )

        t = UI.VContainer(lt, logc, spacing=10)
        return t

    def go(self, cmd):
        if not self._process.is_running():
            self._process = BackgroundProcess(cmd)
            self._process.start()
            rcnt = [cmd]
            if len(self._recent) > 0:
                for x in self._recent:
                    rcnt.append(x)
            if len(rcnt) > 5:
                rcnt = rcnt[:5]
            self._recent = rcnt

    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        self.go(vars.getvalue('cmd', ''))


class ShellProgress(Plugin):
    implements(IProgressBoxProvider)
    title = 'Shell'
    icon = '/dl/shell/icon_small.png'
    can_abort = True
    
    def __init__(self):
        self.proc = self.app.session.get('ShellPlugin-_process')

    def has_progress(self):         
        return self.proc.is_running()
        
    def get_progress(self):
        return self.proc.cmdline
    
    def abort(self):
        self.proc.kill()
   
