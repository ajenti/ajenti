import platform

from ajenti.com import Interface
from ajenti.ui import *
from ajenti.utils import detect_distro, detect_platform
from ajenti.api import *

from api import *

from base64 import b64encode, b64decode


class Dashboard(CategoryPlugin):
    text = 'Dashboard'
    icon = '/dl/dashboard/icon.png'
    folder = 'top'

    widgets = Interface(IDashboardWidget)

    def on_session_start(self):
        self._adding_widget = None

        self._left = []
        self._right = []
        self._widgets = {}
        
        if self.app.config.has_section('dashboard'):
            try:
                self._left = [int(x) for x in self.app.config.get('dashboard', 'left').split(',')]
                self._right = [int(x) for x in self.app.config.get('dashboard', 'right').split(',')]
            except:
                pass
            
            for x in self._left:
                self._widgets[x] = (
                    self.app.config.get('dashboard', '%i-class'%x),
                    eval(b64decode(self.app.config.get('dashboard', '%i-cfg'%x)))
                )

    def fill(self, side, lst, ui, tgt):
        for x in lst:
            try:
                w = self.get_widget(self._widgets[x][0])
                ui.append(tgt, 
                    UI.Widget(
                        w.get_ui(self._widgets[x][1]),
                        pos=side,
                        title=w.title,
                        id=str(x),
                    )
                )
            except:
                raise
                    
    def get_ui(self):
        ui = self.app.inflate('dashboard:main')

        self.fill('l', self._left, ui, 'cleft')
        self.fill('r', self._right, ui, 'cright')

        ui.insertText('host', platform.node())
        ui.insertText('distro', detect_distro())
        ui.find('icon').set('src', '/dl/dashboard/distributor-logo-%s.png'%detect_platform(mapping=False))
        
        if self._adding_widget == True:
            dlg = self.app.inflate('dashboard:add-widget')
            idx = 0
            for prov in self.app.grab_plugins(IDashboardWidget):
                dlg.append('list', UI.ListItem(
                    UI.Image(file=prov.icon),
                    UI.Label(text=prov.name),
                    id=prov.plugin_id,
                ))
                idx += 1
            ui.append('main', dlg)
        elif self._adding_widget != None:
            ui.append(self.get_widget(self._adding_widget).get_config_dialog())
        else:
            ui.append('main', UI.Refresh(time=5000))
            
        return ui

    def add_widget(self, id, cfg):
        w = self.get_widget(id)
        idx = 0
        while idx in self._widgets:
            idx += 1
        self._widgets[idx] = (id, cfg)
        self._left.append(idx)
        self._adding_widget = None
        self.save_cfg()
        
    def save_cfg(self):
        self.app.config.set('dashboard', 'left', ','.join(str(x) for x in self._left))
        self.app.config.set('dashboard', 'right', ','.join(str(x) for x in self._right))
        for x in self._widgets:
            self.app.config.set('dashboard', '%i-class'%x, self._widgets[x][0])
            self.app.config.set(
                'dashboard', '%i-cfg'%x, 
                b64encode(str(self._widgets[x][1]))
            )
        self.app.config.save()

    def get_widget(self, id):
        return self.app.grab_plugins(
           IDashboardWidget, 
           lambda x:x.plugin_id==id,
        )[0]
        
    @event('listitem/click')
    def on_list(self, event, params, vars):
        id = params[0]
        w = self.get_widget(id)
        dlg = w.get_config_dialog()
        if dlg is None:
            self.add_widget(id, None)
        else:
            self._adding_widget = id
        
    @event('button/click')
    def on_button(self, event, params, vars):
        if params[0] == 'btnAddWidget':
            self._adding_widget = True

    @event('dialog/submit')
    def on_dialog(self, event, params, vars):
        if vars.getvalue('action', None) == 'OK':
            id = self._adding_widget
            w = self.get_widget(id)
            cfg = w.process_config(vars)
            self.add_widget(id, cfg)
        else:
            self._adding_widget = None

    @event('widget/move')
    def on_move(self, event, params, vars=None):
        id = int(params[0])
        if params[1] == 'left':
            self._right.remove(id)
            self._left.append(id)
        if params[1] == 'right':
            self._left.remove(id)
            self._right.append(id)
        if params[1] == 'up':
            a = self._left if id in self._left else self._right
            idx = a.index(id)
            if idx > 0:
                a[idx], a[idx-1] = a[idx-1], a[idx]
        if params[1] == 'down':
            a = self._left if id in self._left else self._right
            idx = a.index(id)
            if idx < len(a)-1:
                a[idx], a[idx+1] = a[idx+1], a[idx]
                
        self.save_cfg()
        
