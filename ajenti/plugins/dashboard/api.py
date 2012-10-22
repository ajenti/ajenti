from ajenti.api import *
from ajenti.ui import UIElement, p


@p('config', public=False)
@p('container', type=int, default=0)
@p('index', type=int, default=0)
@interface
class DashboardWidget (BasePlugin, UIElement):
    typeid = 'dashboard:widget'
    name = '---'
    icon = ''

    def save_config(self):
        self.event('save-config')


@interface
class ConfigurableWidget (DashboardWidget):
    def init(self):
        self.on_prepare()
        self.dialog = self.find('config-dialog')
        if not self.config and self.dialog:
            self.config = self.create_config()
            self.on_config_start()
            self.dialog.on('button', self.on_config)
            self.dialog.visible = True
        else:
            self.on_start()

    def on_config(self, button):
        self.dialog.visible = False
        self.on_config_save()
        self.save_config()

    def on_prepare(self):
        pass

    def on_start(self):
        pass

    def create_config(self):
        return None

    def on_config_start(self):
        pass

    def on_config_save(self):
        pass
