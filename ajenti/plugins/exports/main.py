from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import ExportsConfig
from reconfigure.items.exports import ExportData, ClientData


@plugin
class Exports (SectionPlugin):
    def init(self):
        self.title = 'NFS Exports'
        self.icon = 'hdd'
        self.category = 'System'
        self.append(self.ui.inflate('exports:main'))

        self.config = ExportsConfig(path='/etc/exports')
        self.binder = Binder(None, self)
        self.find('exports').new_item = lambda c: ExportData()
        self.find('clients').new_item = lambda c: ClientData()

    def on_page_load(self):
        self.config.load()
        self.binder.reset(self.config.tree).autodiscover().populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
        self.context.notify('info', 'Saved')
