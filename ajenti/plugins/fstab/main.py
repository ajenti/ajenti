import subprocess

import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import FSTabConfig
from reconfigure.items.fstab import FilesystemData

import disks


class Mount (object):
    def __init__(self):
        self.device = ''
        self.mountpoint = ''
        self.type = ''
        self.option = ''


@plugin
class MountsBackend (BasePlugin):
    def __init__(self):
        self.reload()

    def reload(self):
        self.filesystems = []
        try:
            df_data = subprocess.check_output(['df', '-P'])
        except:
            return
            
        for l in df_data.splitlines()[1:]:
            f = Mount()
            l = l.split()
            f.device = l[0]
            if f.device == 'map' and ajenti.platform == 'osx':
                continue
            f.mountpoint = l[5]
            f.used = int(l[2]) * 1024
            f.size = int(l[1]) * 1024
            f.usage = 1.0 * f.used / f.size
            self.filesystems.append(f)


@plugin
class Filesystems (SectionPlugin):
    def init(self):
        self.title = _('Filesystems')
        self.icon = 'hdd'
        self.category = _('System')
        self.append(self.ui.inflate('fstab:main'))

        self.find('type').labels = ['Auto', 'EXT2', 'EXT3', 'EXT4', 'NTFS', 'FAT', 'ZFS', 'ReiserFS', 'Samba', 'None', 'Loop']
        self.find('type').values = ['auto', 'ext2', 'ext3', 'ext4', 'ntfs', 'vfat', 'zfs', 'reiser',  'smb',   'none', 'loop']

        self.fstab_config = FSTabConfig(path='/etc/fstab')
        self.mounts = MountsBackend.get()

        self.binder = Binder(None, self)
        self.find('fstab').find('filesystems').new_item = lambda c: FilesystemData()

        def post_mount_bind(object, collection, item, ui):
            ui.find('umount').on('click', self.on_umount, item)

        self.find('mounts').find('filesystems').post_item_bind = post_mount_bind

    def on_page_load(self):
        self.refresh()

    def on_umount(self, mount):
        subprocess.call(['umount', mount.mountpoint])
        self.context.notify('info', _('Unmounted'))
        self.refresh()

    @on('mount-all', 'click')
    def on_mount_all(self):
        self.save()
        if subprocess.call(['mount', '-a']):
            self.context.notify('error', _('mount -a failed'))
        self.refresh()

    @on('refresh', 'click')
    def refresh(self):
        self.binder.unpopulate()
        self.reload_disks()
        self.fstab_config.load()
        self.fstab = self.fstab_config.tree
        self.mounts.reload()
        self.binder.setup(self).populate()

    def reload_disks(self):
        lst = disks.list_devices(by_uuid=True, by_id=True, by_label=True)
        self.find('device').labels = [x[0] for x in lst]
        self.find('device').values = [x[1] for x in lst]

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.fstab_config.save()
        self.context.notify('info', _('Saved'))
