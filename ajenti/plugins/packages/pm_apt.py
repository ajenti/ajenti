import subprocess

from ajenti.api import *
from api import PackageInfo, PackageManager


@plugin
class DebianPackageManager (PackageManager):
    platforms = ['debian']

    def refresh(self):
        out_u = subprocess.check_output(['apt-show-versions', '-u'])
        out_a = subprocess.check_output(['dpkg', '-l'])
        self.all = self._parse_dpkg(out_a)
        self.all_dict = dict((x.name, x) for x in self.all)
        self.upgradeable = self._parse_asv(out_u)

    def search(self, query):
        out_s = subprocess.check_output(['apt-show-versions', '-a', '-R', query])
        r = []
        found = {}
        for l in out_s.split('\n'):
            s = l.split()
            if len(s) < 4:
                continue

            p = PackageInfo()
            p.name = s[0]
            p.state = 'i' if p.name in self.all_dict else 'r'
            p.version = s[1]

            if not p.name in found or found[p.name] < p.version:
                r.append(p)
                found[p.name] = p.version
        return r

    def get_lists(self):
        self.context.launch('terminal', command='apt-get update')

    def do(self, actions, callback=lambda: 0):
        cmd = 'apt-get install '
        for a in actions:
            cmd += a.name + {'r': '-', 'i': '+'}[a.action] + ' '
        self.context.launch('terminal', command=cmd, callback=callback)

    def _parse_asv(self, d):
        r = []
        for l in d.split('\n'):
            s = l.split('/')
            if len(s) == 0 or not s[0]:
                continue

            p = PackageInfo()
            p.name = s[0]
            p.version = s[1].split(' ')[-1]
            r.append(p)
        return r

    def _parse_apt(self, d):
        r = []
        for l in d.split('\n'):
            s = filter(None, l.split(' '))
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
            s = filter(None, l.split(' '))
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
