import ajenti
from ajenti.api import *
from ajenti.ui import UIElement, p, on
from ajenti.ui.binder import Binder


@p('package')
@p('text', default='This package can be installed automatically')
@plugin
class PackageInstaller (UIElement, BasePlugin):
    typeid = 'packages:installer'

    def init(self):
        self.visible = False
        self.append(self.ui.inflate('packages:installer'))
        self.recheck()

    def recheck(self):
        if ajenti.platform in db:
            apps = db[ajenti.platform]
            if self.package in apps:
                self.pkg = db[ajenti.platform][self.package]
                self.visible = True
                Binder(self, self).autodiscover().populate()

    @on('install', 'click')
    def on_install(self):
        self.event('activate')
        self.context.launch('install-package', package=self.pkg)


db = {
    'debian': {
        'supervisord': 'supervisor',
        'sensors': 'lm-sensors',
        'stunnel': 'stunnel',
    },
    'centos': {
        'supervisord': 'supervisor'
    },
}
