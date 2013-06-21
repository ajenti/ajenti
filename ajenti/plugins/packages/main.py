from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin, intent
from ajenti.ui import on
from ajenti.ui.binder import Binder, CollectionAutoBinding
from ajenti.users import PermissionProvider, restrict
from api import PackageManager, PackageInfo


@plugin
class Packages (SectionPlugin):
    def init(self):
        self.title = _('Packages')
        self.icon = 'gift'
        self.category = _('System')

        self.mgr = PackageManager.get()

        self.append(self.ui.inflate('packages:main'))

        def post_item_bind(object, collection, item, ui):
            ui.find('install').on('click', self.on_install, item)
            ui.find('remove').on('click', self.on_remove, item)
            ui.find('cancel').on('click', self.on_cancel, item)
            ui.find('install').visible = item.action is None
            ui.find('remove').visible = item.action is None and item.state == 'i'
            ui.find('cancel').visible = item.action is not None

        self.find('upgradeable').post_item_bind = post_item_bind
        self.find('search').post_item_bind = post_item_bind
        self.find('pending').post_item_bind = post_item_bind

        self.binder = Binder(None, self.find('bind-root'))
        self.binder_p = Binder(self, self.find('bind-pending'))
        self.binder_s = CollectionAutoBinding([], None, self.find('search')).populate()

        self.pending = {}
        self.installation_running = False
        self.action_queue = []

    def refresh(self):
        self.fill(self.mgr.upgradeable)
        self.binder.reset(self.mgr).autodiscover().populate()
        self.binder_s.unpopulate().populate()
        self._pending = self.pending.values()
        self.binder_p.reset(self).autodiscover().populate()

    def run(self, tasks):
        if self.installation_running:
            self.action_queue += tasks
            self.context.notify('info', _('Enqueueing package installation'))
            return

        self.installation_running = True

        def callback():
            self.installation_running = False
            if self.action_queue:
                self.run(self.action_queue)
                self.action_queue = []
                return
            self.context.notify('info', _('Installation complete!'))

        self.mgr.do(tasks, callback=callback)

    @intent('install-package')
    @restrict('packages:modify')
    def intent_install(self, package):
        #self.activate()
        p = PackageInfo()
        p.name, p.action = package, 'i'
        self.run([p])

    def on_page_load(self):
        self.mgr.refresh()
        self.refresh()

    @restrict('packages:modify')
    def on_install(self, package):
        package.action = 'i'
        self.pending[package.name] = package
        self.refresh()

    @restrict('packages:modify')
    def on_cancel(self, package):
        package.action = None
        if package.name in self.pending:
            del self.pending[package.name]
        self.refresh()

    @restrict('packages:modify')
    def on_remove(self, package):
        package.action = 'r'
        self.pending[package.name] = package
        self.refresh()

    @on('get-lists-button', 'click')
    @restrict('packages:refresh')
    def on_get_lists(self):
        self.mgr.get_lists()

    @on('apply-button', 'click')
    @restrict('packages:modify')
    def on_apply(self):
        self.run(self.pending.values())
        self.pending = {}
        self.refresh()

    @on('upgrade-all-button', 'click')
    @restrict('packages:modify')
    def on_upgrade_all(self):
        for p in self.mgr.upgradeable:
            p.action = 'i'
            self.pending[p.name] = p
        self.refresh()

    @on('cancel-all-button', 'click')
    @restrict('packages:modify')
    def on_cancel_all(self):
        self.pending = {}
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
            self.find('search-counter').text = _('%i found, 100 shown') % len(results)
            results = results[:100]
        else:
            self.find('search-counter').text = _('%i found') % len(results)

        self.fill(results)
        self.binder_s = CollectionAutoBinding(results, None, self.find('search')).populate()


@plugin
class PackagesPermissionsProvider (PermissionProvider):
    def get_name(self):
        return _('Packages')

    def get_permissions(self):
        return [
            ('packages:modify', _('Install / remove')),
            ('packages:refresh', _('Refresh lists')),
        ]
