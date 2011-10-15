#coding: utf-8
from ajenti.ui import *
from ajenti.com import implements, Plugin
from ajenti.api import *
from ajenti import apis
from meters import HDDTempMeter


class HDDTempWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'HDD Temperature'
    icon = '/dl/hddtemp/icon.png'
    name = 'HDD Temperature'
    style = 'linear'

    def get_ui(self, cfg, id=None):
        m = HDDTempMeter(self.app).prepare(cfg)
        self.title = cfg
        return UI.Label(text='%.2f °C'%m.get_value())

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        m = HDDTempMeter(self.app)
        dlg = self.app.inflate('hddtemp:widget-config')
        for s in m.list_disks():
            dlg.append('list', UI.SelectOption(
                value=s,
                text=s,
            ))
        return dlg

    def process_config(self, vars):
        return vars.getvalue('disk', None)
