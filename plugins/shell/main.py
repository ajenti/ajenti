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
        ui = self.app.inflate('shell:main')
        recent = [UI.SelectOption(text=x[0:40] + '...' if len(x) > 40 else x,
                                  value=x) for x in self._recent]
        log = UI.CustomHTML(html=enquote(self._process.output + self._process.errors))

        ui.append('log', log)
        ui.appendAll('shell-recent', *recent)
        
        return ui

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
    icon = '/dl/shell/icon.png'
    can_abort = True
    
    def __init__(self):
        self.proc = self.app.session.get('ShellPlugin-_process')

    def has_progress(self):         
        return self.proc.is_running()
        
    def get_progress(self):
        return self.proc.cmdline
    
    def abort(self):
        self.proc.kill()
   
