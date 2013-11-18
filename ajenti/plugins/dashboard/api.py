from ajenti.api import *
from ajenti.ui import UIElement, p


@p('config', public=False, doc="current configuration dict of this widget instance")
@p('container', type=int, default=0)
@p('index', type=int, default=0)
@interface
class DashboardWidget (BasePlugin, UIElement):
    """
    Base class for widgets (inherits :class:`ajenti.ui.UIElement`).
    """
    typeid = 'dashboard:widget'
    name = '---'
    """ Widget type name """
    icon = None
    """ Widget icon name """
    hidden = False
    """ If True, user will not be able to add this widget through dashboard """

    def save_config(self):
        self.event('save-config')


@interface
class ConfigurableWidget (DashboardWidget):
    """
    Base class for widgets with a configuration dialog
    """
    def init(self):
        self.on_prepare()
        self.dialog = self.find('config-dialog')
        if not self.config and self.dialog:
            self.config = self.create_config()
            self.begin_configuration()            
        else:
            self.on_start()

    def begin_configuration(self):
        self.on_config_start()
        self.dialog.on('button', self.on_config)
        self.dialog.visible = True

    def on_config(self, button):
        self.dialog.visible = False
        self.on_config_save()
        self.save_config()

    def on_prepare(self):
        """
        Widget should create its UI in this method. Called before **self.config** is created
        """

    def on_start(self):
        """
        Widget should populate its UI in this method. **self.config** is now available.
        """

    def create_config(self):
        """
        Should return a default config dict
        """
        return None

    def on_config_start(self):
        """
        Called when user begins to configure the widget. Should populate the config dialog.
        """

    def on_config_save(self):
        """
        Called when user is done configuring the widget.
        """
