from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import shell, enquote
from ajenti.misc import BackgroundProcess


class ShellPlugin(CategoryPlugin):
    text = 'Shell'
    icon = '/dl/shell/icon_small.png'
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
        log = UI.CustomHTML(enquote(self._process.output + self._process.errors))

        frm = UI.FormBox(
                UI.TextInput(name='cmd', size=30, id='shell-command'),
                id='frmRun', hideok=True, hidecancel=True
              )
        frmr = UI.FormBox(
                UI.Select(*recent, name='cmd', id='shell-recent',
                          onclick='shellRecentClick()'),
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
             
        rp = None
        if self._process.is_running():
            rp = UI.VContainer( 
                     UI.HContainer(
                         UI.Image(file='/dl/core/ui/ajax.gif'),
                         UI.Label(text='Running: ' + self._process.cmdline,
                                  size=2),
                         UI.Refresh(time=3000)
                     ),
                     UI.Button(text='Abort command', id='abort')
                 )
             
        t = UI.VContainer(lt, rp, logc, spacing=10)
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

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'abort':
            self._process.kill()

    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        self.go(vars.getvalue('cmd', ''))


class ShellContent(ModuleContent):
    module = 'shell'
    path = __file__
    js_files = ['recent.js']
    
