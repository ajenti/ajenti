from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import FSTabConfig
from reconfigure.items.fstab import FilesystemData

import disks


@plugin
class Filesystems (SectionPlugin):
    def init(self):
        self.title = 'Filesystems'
        self.category = 'System'
        self.append(self.ui.inflate('fstab:main'))

        self.find('type').labels = ['Auto', 'EXT2', 'EXT3', 'EXT4', 'NTFS', 'FAT', 'ZFS', 'ReiserFS', 'None', 'Loop']
        self.find('type').values = ['auto', 'ext2', 'ext3', 'ext4', 'ntfs', 'vfat', 'zfs', 'reiser', 'none', 'loop']

        self.config = FSTabConfig(path='/etc/fstab')
        self.binder = Binder(None, self.find('fstab-config'))
        self.find('filesystems').new_item = lambda c: FilesystemData()

    def on_page_load(self):
        self.reload_disks()
        self.config.load()
        self.binder.reset(self.config.tree).autodiscover().populate()

    def reload_disks(self):
        lst = disks.list_devices(by_uuid=True, by_id=True, by_label=True)
        self.find('device').labels = [x[0] for x in lst]
        self.find('device').values = [x[1] for x in lst]

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
