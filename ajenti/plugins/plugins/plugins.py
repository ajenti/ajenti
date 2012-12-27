import ajenti
from ajenti.api import *
from ajenti.plugins import manager
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder


@plugin
class PluginsPlugin (SectionPlugin):
    def init(self):
        self.title = 'Plugins'
        self.icon = 'cogs'
        self.category = ''
        self.order = 50

        # In case you didn't notice it yet, this is the Plugins Plugin
        self.append(self.ui.inflate('plugins:main'))

        def post_plugin_bind(object, collection, item, ui):
            ui.find('warning-icon').visible = bool(item.crash)
        #self.find('plugins').post_item_bind = post_plugin_bind

        self.binder = Binder(self, self.find('bind-root'))
        self.refresh()

    def refresh(self):
        self.plugins = sorted(manager.get_all().values())
        self.binder.reset().autodiscover().populate()
