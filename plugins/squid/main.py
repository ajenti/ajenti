from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import CategoryPlugin, ModuleContent, EventProcessor, event
from ajenti import apis

from backend import *


class SquidPlugin(apis.services.ServiceControlPlugin):
    text = 'Squid'
    icon = '/dl/squid/icon.png'
    folder = 'servers'
    service_name = 'squid'
    
    def on_session_start(self):
        if not is_installed(): return
        self._tab = 0
        self._cfg = SquidConfig(self.app)
        self._cfg.load()

        self._parts = sorted(self.app.grab_plugins(apis.squid.IPluginPart),
                             key=lambda x: x.weight)

        idx = 0
        for p in self._parts:
            p.init(self, self._cfg, idx)
            idx += 1

    def get_main_ui(self):
        panel = UI.ServicePluginPanel(title='Squid Proxy Server', icon='/dl/squid/icon.png', status=self.service_status, servicename=self.service_name)

        if not is_installed():
            panel.append(UI.VContainer(UI.ErrorBox(title='Error', text='Squid is not installed')))
        else:
            panel.append(self.get_default_ui())

        return panel


    def get_default_ui(self):
        tc = UI.TabControl(active=self._tab)
        for p in self._parts:
            tc.add(p.title, p.get_ui())
        return tc

    @event('button/click')
    @event('minibutton/click')
    def on_click(self, event, params, vars=None):
        for p in self._parts:
            p.on_click(event, params, vars)

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        for p in self._parts:
            p.on_submit(event, params, vars)


class SquidContent(ModuleContent):
    module = 'squid'
    path = __file__
