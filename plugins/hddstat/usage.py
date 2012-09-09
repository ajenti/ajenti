from ajenti.api import *
from ajenti.utils import shell
import os
import re

class DiskUsageMeter(LinearMeter):
    name = 'Disk usage'
    category = 'System'
    transform = 'percent'

    _partstatformat = re.compile('(/dev/)?(?P<dev>\w+)\s+\d+\s+\d+\s+\d+\s+' +
                                       '(?P<usage>\d+)%\s+(?P<mountpoint>\S+)$')
    _totalformat = re.compile('(?P<dev>total)\s+\d+\s+\d+\s+\d+\s+(?P<usage>\d+)%$')

    def init(self):
        if self.variant == 'total':
            self.text = 'total'
        else:
            mountpoints = self.get_mountpoints()
            self.text = '%s (%s)' % (self.variant, ', '.join(mountpoints))

    def _get_stats(self, predicate = (lambda m: True)):
        if hasattr(self, 'variant') and self.variant == 'total':
            matcher = DiskUsageMeter._totalformat
        else:
            matcher = DiskUsageMeter._partstatformat

        stats = shell('df --total')
        matches = []
        for stat in stats.splitlines():
            match = matcher.match(stat)
            if match and predicate(match):
                matches.append(match)
        return matches

    def _get_stats_for_this_device(self):
        return self._get_stats(lambda m: m.group('dev').endswith(self.variant))

    def get_variants(self):
        return sorted(set([ m.group('dev') for m in self._get_stats()])) + ['total']

    def get_mountpoints(self):
        devmatches = self._get_stats_for_this_device()
        return sorted([ m.group('mountpoint') for m in devmatches])

    def get_value(self):
        devmatches = self._get_stats_for_this_device()
        return int(devmatches[0].group('usage'))

    def get_min(self):
        return 0

    def get_max(self):
        return 100
