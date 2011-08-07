from ajenti.api import *
from backend import Backend


class HealthPlugin(CategoryPlugin):
    text = 'Health'
    icon = '/dl/health/icon.png'
    folder = 'top'

    def on_init(self):
        self.backend = Backend(self.app)

    def on_session_start(self):
        self._settings = True#False
        self._configuring = None
        self._configuring_var = None

    def get_ui(self):
        ui = self.app.inflate('health:main')

        if self._settings:
            ui.append('main', self.get_ui_settings())

        if self._configuring:
            mtr = self.backend.get_meter(
                      self._configuring,
                      self._configuring_var
                  )
            ui.append('main', getattr(self, 'get_ui_cfg_%s'%mtr.type)(mtr))

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
        if params[0] == 'btnSettings':
            self._settings = True
        if params[0] == 'config':
            self._configuring = params[1]
            self._configuring_var = params[2]
        if params[0] == 'disable':
            self.backend.del_cfg(*params[1:])

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgSettings':
            self._settings = False
        if params[0] == 'dlgConfigure':
            if vars.getvalue('action', None) == 'OK':
                mtr = self.backend.get_meter(
                          self._configuring,
                          self._configuring_var
                      )
                getattr(self, 'apply_cfg_%s'%(mtr.type))(mtr, vars)
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

    def apply_cfg_binary(self, cls, vars):
        self.backend.set_cfg(cls.plugin_id, cls.variant, {'good_state': vars.getvalue('r-true', True)})

    def apply_cfg_decimal(self, cls, vars):
        self.backend.set_cfg(cls.plugin_id, cls.variant, {
            'limit_susp': float(vars.getvalue('lim_susp', True)),
            'limit_dang': float(vars.getvalue('lim_dang', True)),
        });
