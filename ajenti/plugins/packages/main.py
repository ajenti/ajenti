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

        self.binder = Binder(None, self.find('bind-root'))
        self.binder_s = None

    def on_page_load(self):
        self.mgr.refresh()
        self.binder.reset(self.mgr).autodiscover().populate()

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

        self.binder_s = CollectionAutoBinding(results, None, self.find('search')).populate()
