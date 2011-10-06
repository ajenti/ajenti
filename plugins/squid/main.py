from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti import apis

from backend import *


class SquidPlugin(apis.services.ServiceControlPlugin):
    text = 'Squid'
    icon = '/dl/squid/icon.png'
    folder = 'servers'
    service_name = 'squid'
    
    def get_config(self):
        return self.app.get_config(self._cfg)
        
    def on_session_start(self):
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
        tc = UI.TabControl(active=self._tab)
        for p in self._parts:
            tc.add(p.title, p.get_ui())
        return UI.Pad(tc)

    @event('button/click')
    def on_click(self, event, params, vars=None):
        for p in self._parts:
            p.on_click(event, params, vars)

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        for p in self._parts:
            p.on_submit(event, params, vars)

