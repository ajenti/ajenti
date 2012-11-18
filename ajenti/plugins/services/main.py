from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.ui import p, UIElement
from ajenti.plugins.main.api import SectionPlugin

from api import ServiceMultiplexor


@plugin
class Services (SectionPlugin):
    default_classconfig = {'widgets': []}

    def init(self):
        self.title = 'Services'
        self.category = 'Software'
        self.append(self.ui.inflate('services:main'))
        self.mgr = ServiceMultiplexor.get()
        self.binder = Binder(None, self.find('main'))

        def post_item_bind(object, collection, item, ui):
            ui.find('stop').on('click', self.on_stop, item)
            ui.find('restart').on('click', self.on_restart, item)
            ui.find('start').on('click', self.on_start, item)
            ui.find('stop').visible = item.running
            ui.find('restart').visible = item.running
            ui.find('start').visible = not item.running

        self.find('services').post_item_bind = post_item_bind

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.services = sorted(self.mgr.get_all(), key=lambda x: x.name)
        self.binder.reset(self).autodiscover().populate()

    def on_start(self, item):
        item.start()
        self.refresh()

    def on_stop(self, item):
        item.stop()
        self.refresh()

    def on_restart(self, item):
        item.restart()
        self.refresh()


@p('name')
@plugin
class ServiceControlBar (UIElement):
    typeid = "servicebar"

    def init(self):
        self.append(self.ui.inflate('services:bar'))
        self.find('name').text = self.name

    def on_page_load(self):
        pass
