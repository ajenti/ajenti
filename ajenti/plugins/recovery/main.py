from ajenti.app.api import *
from ajenti import version
from ajenti.com import *
from ajenti.ui import *
from ajenti.utils import detect_distro
from ajenti.app.helpers import *


class RecoveryPlugin(CategoryPlugin):
    text = 'Recovery'
    icon = '/dl/recovery/icon_small.png'
    folder = 'bottom'

    def on_session_start(self):
        self._tab = 0

    def get_ui(self):
        u = UI.PluginPanel(UI.Label(text='Configuration recovery'), title='Configuration recovery', icon='/dl/recovery/icon.png')

        tabs = UI.TabControl(active=self._tab)

        u.append(tabs)
        return u


    @event('button/click')
    @event('minibutton/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        pass
        


class RecoveryContent(ModuleContent):
    path = __file__
    module = 'recovery'
