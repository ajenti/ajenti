from ajenti.api import *
from ajenti.ui import *
from backend import Backend
import trans


class HealthPlugin(CategoryPlugin):
    text = 'Health'
    icon = '/dl/health/icon.png'
    folder = 'top'

    def on_init(self):
        self.backend = Backend(self.app)
        self.mon = ComponentManager.get().find('health-monitor')

    def on_session_start(self):
        self._settings = False
        self._configuring = None

    def get_counter(self):
        lst = ComponentManager.get().find('health-monitor').get()
        return len(filter(lambda x:x!='good', lst.values())) or None

    def get_ui(self):
        ui = self.app.inflate('health:main')

        ostat = 'good'

        stat = { 'good': 'info', 'susp': 'warn', 'dang': 'err' }
        text = { 'good': 'GOOD', 'susp': 'WARNING', 'dang': 'DANGER' }

        for m in sorted(self.mon.get(), key=lambda x:x.name):
            st = self.mon.get()[m]
            if st == 'susp' and ostat == 'good':
                ostat = st
            if st == 'dang':
                ostat = st
            ui.append('list', UI.DataTableRow(
                UI.StatusCell(status=stat[st], text=text[st]),
                UI.DataTableCell(
                    UI.Label(text=m.name, bold=True),
                    UI.Label(text=m.text),
                ),
                UI.Label(
                    text=getattr(trans, 'trans_%s'%m.transform)(m.format_value())
                ),
                UI.DataTableCell(
                    UI.MiniButton(
                        id='config/%s/%s'%(m.plugin_id,m.variant),
                        text='Configure',
                    ),
                ),
            ))

        ui.find('overall').text = 'STATUS: %s'%text[ostat]
        ui.find('overall')['class'] = 'ui-el-status-cell ui-el-status-cell-%s'%stat[ostat]

        if self._settings:
            ui.append('main', self.get_ui_settings())

        if self._configuring:
            ui.append('main', getattr(self, 'get_ui_cfg_%s'%self._configuring.type)(self._configuring))

        return ui

    def get_ui_settings(self):
        ui = self.app.inflate('health:settings')

        for m in self.backend.list_meters():
            for v in self.backend.list_variated(m):
                ui.append('list', UI.DataTableRow(
                    UI.DataTableCell(
                        UI.Label(text=v.name, bold=True),
                        UI.Label(text=v.text),
                    ),
                    UI.DataTableCell(
                        UI.MiniButton(
                            id='config/%s/%s'%(m.plugin_id,v.variant),
                            text='Configure',
                        ),
                        UI.MiniButton(
                            id='disable/%s/%s'%(m.plugin_id,v.variant),
                            text='Disable',
                        ) if self.backend.has_cfg(m.plugin_id,v.variant) else None,
                    ),
                ))
        return ui

    @event('button/click')
    @event('minibutton/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'btnRefresh':
            self.mon.refresh()
        if params[0] == 'btnSettings':
            self._settings = True
        if params[0] == 'config':
            self._configuring = self.backend.get_meter(*params[1:])
        if params[0] == 'disable':
            self.backend.del_cfg(*params[1:])
            self.mon.refresh()

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgSettings':
            self._settings = False
        if params[0] == 'dlgConfigure':
            if vars.getvalue('action', None) == 'OK':
                getattr(self, 'apply_cfg_%s'%(self._configuring.type))(self._configuring, vars)
                self.mon.refresh()
            self._configuring = None

    def get_ui_cfg_binary(self, cls):
        ui = self.app.inflate('health:cfg-binary')
        t = self.backend.get_cfg(cls.plugin_id, cls.variant).setdefault('good_state', True)
        ui.find('r-true').set('checked', t)
        ui.find('r-false').set('checked', not t)
        return ui

    def get_ui_cfg_decimal(self, cls):
        ui = self.app.inflate('health:cfg-decimal')
        c = self.backend.get_cfg(cls.plugin_id, cls.variant)
        ui.find('limit_susp').set('value', str(c.setdefault('limit_susp', 33.0)))
        ui.find('limit_dang').set('value', str(c.setdefault('limit_dang', 66.0)))
        return ui

    def get_ui_cfg_linear(self, cls):
        ui = self.app.inflate('health:cfg-linear')
        c = self.backend.get_cfg(cls.plugin_id, cls.variant)
        ui.find('limit_susp').set('value', str(c.setdefault('limit_susp', 33.0)))
        ui.find('limit_dang').set('value', str(c.setdefault('limit_dang', 66.0)))
        ui.find('max').set('text', 'Min: %.2f, max: %.2f'%(cls.get_min(), cls.get_max()))
        return ui

    def apply_cfg_binary(self, cls, vars):
        self.backend.set_cfg(cls.plugin_id, cls.variant, {'good_state': eval(vars.getvalue('val', 'True'))})

    def apply_cfg_decimal(self, cls, vars):
        self.backend.set_cfg(cls.plugin_id, cls.variant, {
            'limit_susp': float(vars.getvalue('lim_susp', True)),
            'limit_dang': float(vars.getvalue('lim_dang', True)),
        });

    apply_cfg_linear = apply_cfg_decimal
