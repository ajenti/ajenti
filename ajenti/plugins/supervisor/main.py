from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on

from reconfigure.configs import SupervisorConfig
from reconfigure.builders.supervisor import ProgramBuilder

from client import Client


@plugin
class Supervisor (SectionPlugin):
    def init(self):
        self.title = 'Supervisor'
        self.category = 'Software'
        self.append(self.ui.inflate('supervisor:main'))
        self._client = Client.get()
        self.binder = Binder(None, self.find('main'))

        def post_item_bind(object, collection, item, ui):
            saved = hasattr(item, 'running')
            ui.find('stop').on('click', self.on_stop, item)
            ui.find('restart').on('click', self.on_restart, item)
            ui.find('start').on('click', self.on_start, item)
            ui.find('stop').visible = saved and item.running
            ui.find('restart').visible = saved and item.running
            ui.find('start').visible = saved and not item.running

        self.find('programs').post_item_bind = post_item_bind
        self.find('programs').new_item = lambda c: ProgramBuilder.empty()
        self.config = SupervisorConfig(path='/etc/supervisor/supervisord.conf')

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self._client.fill(self.config.tree.programs)
        self.binder.reset(self.config.tree).autodiscover().populate()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        self.config.save()
        self.refresh()

    def on_start(self, item):
        self._client.start(item.name)
        self.refresh()

    def on_stop(self, item):
        self._client.stop(item.name)
        self.refresh()

    def on_restart(self, item):
        self._client.restart(item.name)
        self.refresh()
