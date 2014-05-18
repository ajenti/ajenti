import os
import re
import psutil
import shutil
import statvfs

from ajenti.api import *
from ajenti.api.sensors import Sensor


def list_devices(by_name=True, by_uuid=False, by_id=False, by_label=False):
    result = []

    def add_dir(path, namefx=lambda s, r: s, valuefx=lambda s, r: r):
        if os.path.exists(path):
            for s in os.listdir(path):
                rp = os.path.realpath(os.path.join(path, s))
                result.append((namefx(s, rp), valuefx(s, rp)))

    for s in os.listdir('/dev'):
        if re.match('sd.$|hd.$|scd.$|fd.$|ad.+$', s):
            result.append((s, '/dev/' + s))

    if by_uuid:
        add_dir('/dev/disk/by-uuid', lambda s, r: '%s: UUID %s' % (r, s), lambda s, r: 'UUID=%s' % s)

    if by_label:
        add_dir('/dev/disk/by-label', lambda s, r: 'Label "%s"' % s, lambda s, r: 'LABEL=%s' % s)

    if by_id:
        add_dir('/dev/disk/by-id', lambda s, r: '%s: %s' % (r, s))

    return sorted(result, key=lambda x: x[0])


@plugin
class PSUtilDiskUsageSensor (Sensor):
    id = 'disk-usage'
    timeout = 5

    @classmethod
    def __list_partitions(cls):
        return filter(lambda p: p.device, psutil.disk_partitions(True))
    
    @classmethod
    def verify(cls):
        try:
            return len(cls.__list_partitions()) > 0
        except:
            return False

    def get_variants(self):
        return sorted([x.mountpoint for x in self.__list_partitions()])

    def measure(self, path):
        try:
            if path:
                v = psutil.disk_usage(path)
            else:
                return (0, 1)
        except OSError:
            return (0, 1)
        return (v.used, v.free, v.total)


@plugin
class MTabDiskUsageSensor (Sensor):
    """
    Useful for procfs-less virtualization containers
    """
    id = 'disk-usage'
    timeout = 5

    @classmethod
    def verify(cls):
        return os.path.exists('/etc/mtab')

    def get_variants(self):
        return filter(lambda x: x != 'none', sorted(l.split()[1] for l in open('/etc/mtab')))

    def measure(self, path):
        s = os.statvfs(path)
        total = s[statvfs.F_FRSIZE] * s[statvfs.F_BLOCKS]
        free = s[statvfs.F_BFREE] * s[statvfs.F_BSIZE]
        return (total - free, free, total)
        