from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder, CollectionAutoBinding

from api import PackageManager


@plugin
class Packages (SectionPlugin):
    def init(self):
        self.title = 'Packages'
        self.category = 'System'

        self.mgr = PackageManager.get()

        self.append(self.ui.inflate('packages:main'))

        def post_item_bind(object, collection, item, ui):
            ui.find('install').on('click', self.on_install, item)
            ui.find('remove').on('click', self.on_remove, item)
            ui.find('cancel').on('click', self.on_cancel, item)
            ui.find('install').visible = item.action == None
            ui.find('remove').visible = item.action == None and item.state == 'r'
            ui.find('cancel').visible = item.action != None

        self.find('upgradeable').post_item_bind = post_item_bind
        self.find('search').post_item_bind = post_item_bind
        self.find('pending').post_item_bind = post_item_bind

        self.binder = Binder(None, self.find('bind-root'))
        self.binder_p = Binder(self, self.find('bind-pending'))
        self.binder_s = CollectionAutoBinding([], None, self.find('search')).populate()

        self.pending = {}

    def refresh(self):
        self.fill(self.mgr.upgradeable)
        self.binder.reset(self.mgr).autodiscover().populate()
        self.binder_s.unpopulate().populate()
        self._pending = self.pending.values()
        self.binder_p.reset(self).autodiscover().populate()

    def on_page_load(self):
        self.mgr.refresh()
        self.refresh()

    def on_install(self, package):
        package.action = 'i'
        self.pending[package.name] = package
        self.refresh()

    def on_cancel(self, package):
        package.action = None
        if package.name in self.pending:
            del self.pending[package.name]
        self.refresh()

    def on_remove(self, package):
        package.action = 'r'
        self.pending[package.name] = package
        self.refresh()

    def fill(self, packages):
        for p in packages:
            if p.name in self.pending:
                p.action = self.pending[p.name].action

    @on('search-button', 'click')
    def on_search(self):
        query = self.find('search-box').value
        results = self.mgr.search(query)
        if self.binder_s:
            self.binder_s.unpopulate()
        if len(results) > 100:
            self.find('search-counter').text = '%i found, 100 shown' % len(results)
            results = results[:100]
        else:
            self.find('search-counter').text = '%i found' % len(results)

        self.fill(results)
        self.binder_s = CollectionAutoBinding(results, None, self.find('search')).populate()
