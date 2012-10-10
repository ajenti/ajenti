from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder

from reconfigure.configs import NginxConfig


@plugin
class Configurator (SectionPlugin):
    def init(self):
        self.title = 'nginx'
        self.category = 'Software'
        
        self.append(self.ui.inflate('nginx:main'))

        self.config = NginxConfig(path='/etc/nginx/nginx.conf')
        self.config.load()

        self.binder = Binder(self.config.tree, self.find('nginx-config'))
        self.binder.autodiscover()
        self.binder.populate()

        self.find('save').on('click', self.save)

    def save(self):
        self.binder.update()
        self.config.save()
        self.publish()
