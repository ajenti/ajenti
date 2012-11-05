import os
import re
import subprocess

from ajenti.api import *
from ajenti.api.sensors import Sensor


def list_devices(by_name=True, by_uuid=False, by_id=False, by_label=False):
    result = []

    def add_dir(path, namefx=lambda s, r: s, valuefx=lambda s, r: r):
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
class DiskUsageSensor (Sensor):
    id = 'disk-usage'
    timeout = 30

    _partstatformat = re.compile('(/dev/)?(?P<dev>\w+)\s+\d+\s+\d+\s+\d+\s+' +
                                       '(?P<usage>\d+)%\s+(?P<mountpoint>\S+)$')
    _totalformat = re.compile('(?P<dev>total)\s+\d+\s+\d+\s+\d+\s+(?P<usage>\d+)%$')

    def _get_stats(self, predicate=(lambda m: True)):
        if hasattr(self, 'variant') and self.variant == 'total':
            matcher = self._totalformat
        else:
            matcher = self._partstatformat

        stats = subprocess.check_output(['df', '--total'])
        matches = []
        for stat in stats.splitlines():
            match = matcher.match(stat)
            if match and predicate(match):
                matches.append(match)
        return matches

    def get_variants(self):
        return sorted(set([m.group('dev') for m in self._get_stats()])) + ['total']

    def measure(self, device):
        devmatches = self._get_stats(lambda m: m.group('dev').endswith(device))
        if not devmatches:
            return 0
        return int(devmatches[0].group('usage'))
