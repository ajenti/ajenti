import subprocess

from ajenti.api import *


class PackageInfo (object):
    def __init__(self):
        self.name = ''
        self.state = 'r'
        self.action = None
        self.version = ''
        self.description = ''

    @property
    def _icon(self):
        return 'ok' if self.state == 'i' else None


@interface
class PackageManager (BasePlugin):
    def init(self):
        self.upgradeable = []

    def refresh(self):
        pass


@plugin
class DebianPackageManager (PackageManager):
    def refresh(self):
        out_u = subprocess.check_output(['apt-get', 'upgrade', '-s', '-qq'])
        out_a = subprocess.check_output(['dpkg', '-l'])
        self.all = self._parse_dpkg(out_a)
        self.all_dict = dict((x.name, x) for x in self.all)
        self.upgradeable = sorted(filter(lambda x: x.action == 'i', self._parse_apt(out_u)), key=lambda x: x.name)

    def search(self, query):
        out_s = subprocess.check_output(['apt-cache', 'search', query])
        r = []
        for l in out_s.split('\n'):
            s = l.split()
            if len(s) == 0:
                continue

            p = PackageInfo()
            p.name = s[0]
            p.state = 'i' if p.name in self.all_dict else 'r'
            p.description = ' '.join(s[2:])
            r.append(p)
        return r

    def _parse_apt(self, d):
        r = []
        for l in d.split('\n'):
            s = l.split()
            if len(s) == 0:
                continue

            p = PackageInfo()
            if s[0] == 'Inst':
                p.action = 'i'
            elif s[0] in ['Remv', 'Purg']:
                p.action = 'r'
            else:
                continue
            p.name = s[1]
            p.version = s[2].strip('[]')
            r.append(p)
        return r

    def _parse_dpkg(self, d):
        r = []
        for l in d.split('\n'):
            s = l.split()
            if len(s) == 0:
                continue

            p = PackageInfo()
            if s[0][0] == 'i':
                p.state = 'i'
            else:
                continue

            p.name = s[1]
            p.version = s[2]
            p.description = ' '.join(s[3:])
            r.append(p)
        return r
