import platform

from ajenti.com import Interface
from ajenti.ui import UI
from ajenti.utils import detect_distro, detect_platform
from ajenti.api import *
from ajenti import apis


class Dashboard(CategoryPlugin):
    text = 'Dashboard'
    icon = '/dl/dashboard/icon.png'
    folder = 'top'

    def on_session_start(self):
        self._adding_widget = None
        self._mgr = apis.dashboard.WidgetManager(self.app)

    def fill(self, side, lst, ui, tgt):
        for x in lst:
            try:
                w = self._mgr.get_widget_object(x)
                if not w:
                    continue
                ui.append(tgt,
                    UI.Widget(
                        w.get_ui(self._mgr.get_widget_config(x), id=str(x)),
                        pos=side,
                        icon=w.icon,
                        style=w.style,
                        title=w.title,
                        id=str(x),
                    )
                )
            except:
                raise

    def get_ui(self):
        ui = self.app.inflate('dashboard:main')
        self._mgr.refresh()

        self.fill('l', self._mgr.list_left(), ui, 'cleft')
        self.fill('r', self._mgr.list_right(), ui, 'cright')

        ui.insertText('host', platform.node())
        ui.insertText('distro', detect_distro())
        ui.find('icon').set('src', '/dl/dashboard/distributor-logo-%s.png'%detect_platform(mapping=False))

        if self._adding_widget == True:
            dlg = self.app.inflate('dashboard:add-widget')
            idx = 0
            for prov in sorted(self.app.grab_plugins(apis.dashboard.IWidget)):
                if hasattr(prov, 'hidden'):
                    continue
                dlg.append('list', UI.ListItem(
                    UI.HContainer(
                        UI.Image(file=prov.icon),
                        UI.Label(text=prov.name),
                    ),
                    id=prov.plugin_id,
                ))
                idx += 1
            ui.append('main', dlg)

        elif self._adding_widget != None:
            ui.append('main', self._mgr.get_by_name(self._adding_widget).get_config_dialog())

        return ui

    @event('listitem/click')
    def on_list(self, event, params, vars):
        id = params[0]
        w = self._mgr.get_by_name(id)
        dlg = w.get_config_dialog()
        if dlg is None:
            self._mgr.add_widget(id, None)
            self._adding_widget = None
        else:
            self._adding_widget = id

    @event('dashboard/save')
    def on_save(self, event, params, vars):
        l = params[0]
        r = params[1]
        l = [int(x) for x in l.split(',') if x]
        r = [int(x) for x in r.split(',') if x]
        self._mgr.reorder(l,r)

    @event('button/click')
    @event('linklabel/click')
    def on_event(self, event, params, vars):
        if params[0] == 'btnAddWidget':
            self._adding_widget = True
        try:
            wid = int(params[0])
            params = params[1:]
            self._mgr.get_widget_object(wid).\
                handle(event, params, self._mgr.get_widget_config(wid), vars)
        except:
            pass

    @event('dialog/submit')
    def on_dialog(self, event, params, vars):
        if params[0] == 'dlgAddWidget':
            self._adding_widget = None
        if params[0] == 'dlgWidgetConfig':
            if vars.getvalue('action', None) == 'OK':
                id = self._adding_widget
                w = self._mgr.get_by_name(id)
                cfg = w.process_config(vars)
                self._mgr.add_widget(id, cfg)
            self._adding_widget = None
