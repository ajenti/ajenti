import subprocess

from ajenti.api import *
from api import PackageInfo, PackageManager


@plugin
class ArchPackageManager (PackageManager):
    platforms = ['arch']

    def init(self):
        self.upgradeable = []
        self.all = []

    def get_lists(self):
        self.context.launch('terminal', command='pacman -Sy')

    def refresh(self):
        out_u = subprocess.check_output(['pacman', '-Qu'])
        out_a = subprocess.check_output(['pacman', '-Qs'])
        self.upgradeable = self._parse_upgradeable(out_u)

        self.all = self._parse_all_installed(out_a)
        self.all_dict = dict((x.name, x) for x in self.all)

    def search(self, query):
        return []

    def do(self, actions):
        to_install = [a for a in actions if a.action == 'i']
        to_remove = [a for a in actions if a.action == 'r']
        cmd = ''
        if len(to_install) > 0:
            cmd += 'pacman -S ' + ' '.join(a.name for a in to_install)
            if len(to_remove) > 0:
                cmd += ' && '
        if len(to_remove) > 0:
            cmd += 'pacman -R ' + ' '.join(a.name for a in to_remove)
        self.context.launch('terminal', command=cmd, callback=callback)


    def _parse_upgradeable(self, d):
        r = []
        for l in d.split('\n'):
            s = l.split(' ')
            if len(s) == 1:
                continue

            p = PackageInfo()
            p.action = 'i'

            p.name = s[0]
            p.version = s[1]
            r.append(p)
        return r

    def _parse_all_installed(self, d):
        r = []

        lines = d.splitlines()
        infos = ['\n'.join(lines[i:i+2]) for i in range(0, len(lines), 2)]

        for info in infos:
            s = info.split('\n')
            if len(s) == 0:
                continue

            package = s[0].split(' ')

            p = PackageInfo()
            p.state = 'i'

            p.name = package[0]
            p.version = package[1]

            s[1].lstrip().rstrip()
            p.description = ' '.join(s[1])

            r.append(p)
        return r

