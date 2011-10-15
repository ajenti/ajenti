from ajenti.ui import *
from ajenti import apis
from ajenti.com import implements, Plugin
from ajenti.api import *


class HealthWidget(Plugin):
    implements(apis.dashboard.IWidget)
    title = 'Health'
    icon = '/dl/health/icon.png'
    name = 'Health monitor'
    style = 'linear'

    def get_ui(self, cfg, id=None):
        self.mon = ComponentManager.get().find('health-monitor')
        text = { 'good': 'GOOD', 'susp': 'WARNING', 'dang': 'DANGER' }
        stat = { 'good': 'info', 'susp': 'warn', 'dang': 'err' }
        ostat = 'good'
        for m in sorted(self.mon.get(), key=lambda x:x.name):
            st = self.mon.get()[m]
            if st == 'susp' and ostat == 'good':
                ostat = st
            if st == 'dang':
                ostat = st

        ui = self.app.inflate('health:widget')
        ui.find('overall').text = text[ostat]
        ui.find('overall')['class'] = 'ui-el-status-cell ui-el-status-cell-%s'%stat[ostat]
        return ui

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        pass

    def process_config(self, vars):
        pass
