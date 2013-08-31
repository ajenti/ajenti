from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.ui import p, UIElement, on
from ajenti.plugins.main.api import SectionPlugin

from api import ServiceMultiplexor


@plugin
class Services (SectionPlugin):
    def init(self):
        self.title = _('Services')
        self.icon = 'play'
        self.category = _('Software')
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
        self.context.notify('info', _('%s started') % item.name)

    def on_stop(self, item):
        item.stop()
        self.refresh()
        self.context.notify('info', _('%s stopped') % item.name)

    def on_restart(self, item):
        item.restart()
        self.refresh()
        self.context.notify('info', _('%s restarted') % item.name)


@p('name', bindtypes=[str, unicode])
@p('buttons', default=[], type=eval)
@plugin
class ServiceControlBar (UIElement):
    typeid = 'servicebar'

    def init(self):
        self.service = None
        self.reload()

    def reload(self):
        self.empty()
        self.append(self.ui.inflate('services:bar'))
        if self.name:
            self.service = ServiceMultiplexor.get().get_one(self.name)
            for btn in self.buttons:
                b = self.ui.create('button')
                b.text, b.icon = btn['text'], btn['icon']
                b.on('click', self.on_command, btn['command'])
                self.find('buttons').append(b)
            self.refresh()

    def on_page_load(self):
        self.reload()

    def refresh(self):
        if self.service:
            self.service.refresh()
            self.find('start').visible = not self.service.running
            self.find('stop').visible = self.service.running
            self.find('restart').visible = self.service.running

    @on('start', 'click')
    def on_start(self):
        self.service.start()
        self.on_page_load()

    @on('restart', 'click')
    def on_restart(self):
        self.service.restart()
        self.on_page_load()

    @on('stop', 'click')
    def on_stop(self):
        self.service.stop()
        self.on_page_load()

    def on_command(self, cmd):
        self.service.command(cmd)
        self.on_page_load()
