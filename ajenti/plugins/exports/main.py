import os

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import ExportsConfig
from reconfigure.items.exports import ExportData, ClientData


@plugin
class Exports (SectionPlugin):
    config_path = '/etc/exports'

    def init(self):
        self.title = _('NFS Exports')
        self.icon = 'hdd'
        self.category = _('Software')
        self.append(self.ui.inflate('exports:main'))

        if not os.path.exists(self.config_path):
            open(self.config_path, 'w').close()

        self.config = ExportsConfig(path=self.config_path)
        self.binder = Binder(None, self)
        self.find('exports').new_item = lambda c: ExportData()
        self.find('clients').new_item = lambda c: ClientData()

    def on_page_load(self):
        self.config.load()
        self.binder.setup(self.config.tree).populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
        self.context.notify('info', _('Saved'))
