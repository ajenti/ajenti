import os

from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on

from reconfigure.configs import NetatalkConfig
from reconfigure.items.netatalk import ShareData


@plugin
class Netatalk (SectionPlugin):
    config_path = '/etc/afp.conf'

    def init(self):
        self.title = 'Netatalk'
        self.icon = 'folder-close'
        self.category = _('Software')
        self.append(self.ui.inflate('netatalk:main'))

        if not os.path.exists(self.config_path):
            open(self.config_path, 'w').write("[Global]")

        self.binder = Binder(None, self.find('config'))
        self.find('shares').new_item = lambda c: ShareData()
        self.config = NetatalkConfig(path=self.config_path)

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self.binder.reset(self.config.tree).autodiscover().populate()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        self.config.save()
        self.refresh()
