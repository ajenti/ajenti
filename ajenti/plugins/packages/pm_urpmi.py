import subprocess

from ajenti.api import *
from api import PackageInfo, PackageManager


@plugin
@rootcontext
@persistent
class UrpmiPackageManager (PackageManager):
    platforms = ['mageia']
    def refresh(self):
        try:
            out_update = subprocess.check_output(['urpmi.update', '-a'])
        except subprocess.CalledProcessError as e:
            pass

        try:
            out_u = subprocess.check_output(['urpmq', '--auto-select', "-r"])
            self.upgradeable = self._parse_urpmi(out_u)
        except subprocess.CalledProcessError as e:
            self.upgradeable = []

        try:
            out_a = subprocess.check_output(['urpmq', '--list', "-r"])
            self.all = self._parse_urpmi(out_a)
            self.all_dict = dict((x.name, x) for x in self.all)
        except subprocess.CalledProcessError as e:
            self.all = []
            self.all_dict = {}

    def search(self, query):
        if query.strip() == "":
            return []
        try:
            out_s = subprocess.check_output([
                'urpmq', "-Y",
                "--summary", query
            ])
        except subprocess.CalledProcessError as e:
            return []
        
        r = []
        for l in out_s.split('\n'):
            s = l.strip().split(":", 1)
            if len(s) != 2:
                continue
            summary_list = s[1].rsplit("(",1)
            if len(summary_list) != 2:
                continue
            p = PackageInfo()
            p.name = s[0].strip()
            p.summary = summary_list[0].strip()
            p.version = summary_list[1].rsplit(")",1)[0].strip()
            p.state = 'r'
            if p.name in self.all_dict and self.all_dict[p.name].state == 'i':
                p.state = 'i'
            r.append(p)
        return r
    def get_lists(self):
        self.context.launch(
            'terminal',
            command='urpmi.update -a ; read -p "Press [enter] to continue"'
        )

    def do(self, actions, callback=lambda: 0):
        to_install = [a for a in actions if a.action == 'i']
        to_remove = [a for a in actions if a.action == 'r']
        cmd = ''
        if len(to_install) > 0:
            cmd += 'urpmi ' + ' '.join(a.name for a in to_install)
            if len(to_remove) > 0:
                cmd += ' && '
        if len(to_remove) > 0:
            cmd += 'urpme ' + ' '.join(a.name for a in to_remove)
        if len(to_install) > 0 or len(to_remove) > 0:
            cmd += " ; "
        cmd += 'read -p "Press [enter] to continue"'
        self.context.launch('terminal', command=cmd, callback=callback)

    def _parse_urpmi(self, ss):
        r = []
        for s in ss.splitlines():
            s = s.strip().rsplit("-", 2)
            if len(s) != 3:
                continue
            try:
                p = PackageInfo()
                p.name = s[0]
                p.version = "-".join(s[1:])
                p.state = 'i'
                r.append(p)
                if len(r.keys()) > 2500:
                    break
            except:
                pass
        return r
