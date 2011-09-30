from ajenti.com import Plugin, Interface, implements
from ajenti.api import Component
from ajenti.apis import API
from base64 import b64encode, b64decode


class IDashboardWidget(Interface): # TODO: remove in favor of ajenti.apis
    title = ''
    name = ''
    icon = ''
    style = 'normal'

    def get_ui(self, cfg, id=None):
        pass

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        pass

    def process_config(self, vars):
        pass


class Dashboard (API):
    IWidget = IDashboardWidget


    class WidgetManager (Plugin):
        def __init__(self):
            self.refresh()

        def refresh(self):
            self._left = []
            self._right = []
            self._widgets = {}

            try:
                self._left = [int(x) for x in self.app.config.get('dashboard', 'left').split(',')]
                self._right = [int(x) for x in self.app.config.get('dashboard', 'right').split(',')]
            except:
                pass

            for x in (self._left + self._right):
                self._widgets[x] = (
                    self.app.config.get('dashboard', '%i-class'%x),
                    eval(b64decode(self.app.config.get('dashboard', '%i-cfg'%x)))
                )

        def list_left(self): return self._left
        def list_right(self): return self._right

        def add_widget(self, id, cfg):
            if id.__class__ is not str:
                id = id.plugin_id
            idx = 0
            while idx in self._widgets:
                idx += 1
            self._widgets[idx] = (id, cfg)
            self._left.append(idx)
            self.save_cfg()

        def reorder(self, nl, nr):
            self._left = nl
            self._right = nr
            self.save_cfg()

        def remove_widget(self, id):
            if id in self._right:
                self._right.remove(id)
            else:
                self._left.remove(id)
            del self._widgets[id]
            self.app.config.remove_option('dashboard', '%i-class'%id)
            self.app.config.remove_option('dashboard', '%i-cfg'%id)
            self.save_cfg()

        def save_cfg(self):
            self.app.config.set('dashboard', 'left', ','.join(str(x) for x in self._left))
            self.app.config.set('dashboard', 'right', ','.join(str(x) for x in self._right))
            for x in self._widgets:
                self.app.config.set('dashboard', '%i-class'%x, self._widgets[x][0])
                self.app.config.set(
                    'dashboard', '%i-cfg'%x,
                    b64encode(repr(self._widgets[x][1]))
                )
            self.app.config.save()

        def get_widget_object(self, id):
            return self.get_by_name(self._widgets[id][0])

        def get_widget_config(self, id):
            return self._widgets[id][1]

        def get_by_name(self, id):
            try:
                return self.app.grab_plugins(
                   IDashboardWidget,
                   lambda x:x.plugin_id==id,
                )[0]
            except:
                return None
