import subprocess

from ajenti.api import *
from api import PackageInfo, PackageManager


@plugin
class YumPackageManager (PackageManager):
    platforms = ['centos']

    def refresh(self):
        try:
            out_u = subprocess.check_output(['yum', '-C', '-q', '-d0', '-e0', 'check-update'])
        except subprocess.CalledProcessError as e:
            # yum check-update returns 100 if there are packages available for an update
            if e.returncode == 100:
                out_u = e.output
            else:
                raise e
        out_a = subprocess.check_output(['yum', '-C', '-d0', '-e0', 'list', 'installed', '-q'])
        self.all = self._parse_yum(out_a)
        self.all_dict = dict((x.name, x) for x in self.all)
        self.upgradeable = self._parse_yum(out_u)

    def search(self, query):
        out_s = subprocess.check_output(['yum', '-C', '-q', '-d0', '-e0', 'search', query])
        r = []
        for l in out_s.split('\n'):
            s = l.split()
            if len(s) < 2:
                continue
            if s[0].startswith('====') or s[0] == ':':
                continue
            else:
                p = PackageInfo()
                p.name = s[0]
                p.state = 'r'
                if p.name in self.all_dict and self.all_dict[p.name].state == 'i':
                    p.state = 'i'
                r.append(p)
        return r

    def get_lists(self):
        self.context.launch('terminal', command='yum check-update')

    def do(self, actions, callback=lambda: 0):
        to_install = [a for a in actions if a.action == 'i']
        to_remove = [a for a in actions if a.action == 'r']
        cmd = ''
        if len(to_install) > 0:
            cmd += 'yum install ' + ' '.join(a.name for a in to_install)
            if len(to_remove) > 0:
                cmd += ' && '
        if len(to_remove) > 0:
            cmd += 'yum remove ' + ' '.join(a.name for a in to_remove)
        self.context.launch('terminal', command=cmd, callback=callback)

    def _parse_yum(self, ss):
        r = []
        for s in ss.splitlines():
            s = s.split()
            try:
                if s[0] == '':
                    continue
                else:
                    p = PackageInfo()
                    p.name = s[0]
                    p.state = 'i'
                    r.append(p)
                if len(r.keys()) > 250:
                    break
            except:
                pass
        return r
