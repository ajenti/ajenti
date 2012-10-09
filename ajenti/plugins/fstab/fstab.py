from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder

from reconfigure.configs import FSTabConfig
from reconfigure.items.fstab import Filesystem


@plugin
class Filesystems (SectionPlugin):
    def init(self):
        self.title = 'Filesystems'
        self.append(self.ui.inflate('fstab:main'))

        self.config = FSTabConfig(path='/etc/fstab')
        self.config.load()
        self.binder = Binder(self.config.tree, self.find('fstab-config'))
        self.find('filesystems').new_item = lambda c: Filesystem()
        self.find('device').items = ['1', '2', '3']
        self.find('device').values = ['a', 'b', 'c']
        self.binder.autodiscover()
        self.binder.populate()

        self.find('save').on('click', self.save)

    def save(self):
        self.binder.update()
        self.config.save()
        self.publish()
