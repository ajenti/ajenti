from ajenti.api import *
from ajenti.plugins import manager, ModuleDependency, BinaryDependency
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder


@plugin
class PluginsPlugin (SectionPlugin):
    def init(self):
        self.title = _('Plugins')
        self.icon = 'cogs'
        self.category = ''
        self.order = 60

        # In case you didn't notice it yet, this is the Plugins Plugin Plugin
        self.append(self.ui.inflate('plugins:main'))

        def post_plugin_bind(object, collection, item, ui):
            if not item.crash:
                ui.find('crash').visible = False

        def post_dep_bind(object, collection, item, ui):
            if not item.satisfied():
                installer = ui.find('fix')
                if item.__class__ == ModuleDependency:
                    installer.package = 'python-module-' + item.module_name
                if item.__class__ == BinaryDependency:
                    installer.package = item.binary_name
                installer.recheck()

        self.find('plugins').post_item_bind = post_plugin_bind
        self.find('dependencies').post_item_bind = post_dep_bind

        self.binder = Binder(None, self.find('bind-root'))

    def on_page_load(self):
        self.context.endpoint.send_progress(_('Gathering plugin list'))
        self.plugins = sorted(manager.get_all().values())
        self.binder.setup(self).populate()
