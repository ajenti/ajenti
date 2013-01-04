import ajenti
from ajenti.api import *
from ajenti.plugins import manager, ModuleDependency, BinaryDependency
from ajenti.plugins.main.api import SectionPlugin
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

        def post_dep_bind(object, collection, item, ui):
            if item.__class__ == ModuleDependency and ajenti.platform in self.known_modules:
                mods = self.known_modules[ajenti.platform]
                if item.module_name in mods:
                    ui.find('fix-module').visible = True
                    ui.find('fix-module').on('click', self.install_package, mods[item.module_name])
            if item.__class__ == BinaryDependency and ajenti.platform in self.known_apps:
                mods = self.known_apps[ajenti.platform]
                if item.binary_name in mods:
                    ui.find('fix-module').visible = True
                    ui.find('fix-module').on('click', self.install_package, mods[item.binary_name])

        self.find('dependencies').post_item_bind = post_dep_bind

        self.binder = Binder(self, self.find('bind-root'))
        self.refresh()

    def install_package(self, module):
        self.context.launch('install-package', package=module)

    def refresh(self):
        self.plugins = sorted(manager.get_all().values())
        self.binder.reset().autodiscover().populate()

    known_modules = {
        'debian': {
            'lolz': 'python-lolz'
        },
    }

    known_apps = {
        'debian': {
            'supervisord': 'supervisor'
        },
        'centos': {
            'supervisord': 'supervisor'
        },
    }
