import os
import subprocess

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis


class PacmanPackageManager(Plugin):
    implements(apis.pkgman.IPackageManager)
    platform = ['Arch']

    _pending = {}

    def refresh(self, st):
        a = self._get_all()
        st.upgradeable = self._parse_pm_u(shell('pacman -Qu').splitlines())

        st.pending = {}
        try:
            ss = open('/tmp/ajenti-pacman-pending.list', 'r').read().splitlines()
            for s in ss:
                s = s.split()
                try:
                    st.pending[s[1]] = s[0]
                except:
                    pass
        except:
            pass

        st.full = a

    def get_lists(self):
        cmd = 'pacman -Sy > /tmp/ajenti-pacman-output; rm -f /tmp/ajenti-pacman-output &'
        subprocess.Popen(['bash', '-c', cmd])

    def search(self, q, st):
        return self._parse_pm(shell('pacman -Ss %s' % q).splitlines())

    def mark_install(self, st, name):
        st.pending[name] = 'install'
        self._save_pending(st.pending)

    def mark_remove(self, st, name):
        st.pending[name] = 'remove'
        self._save_pending(st.pending)

    def mark_cancel(self, st, name):
        del st.pending[name]
        self._save_pending(st.pending)

    def apply(self, st):
        fcmd = '('
        
        cmd = 'pacman -S --noconfirm '
        a = False
        for x in st.pending:
            if st.pending[x] == 'install':
                cmd += x + ' '
                a = True
                
        if a:
            fcmd += cmd + '; '
        
        cmd = 'pacman -Rc --noconfirm '
        a = False
        for x in st.pending:
            if st.pending[x] != 'install':
                cmd += x + ' '
                a = True

        if a:
            fcmd += cmd
        
        fcmd += ') > /tmp/ajenti-pacman-output; rm -f /tmp/ajenti-pacman-output &'
        subprocess.Popen(['bash', '-c', fcmd])

    def is_busy(self):
        if shell_status('pgrep pacman') != 0: return False
        return os.path.exists('/tmp/ajenti-pacman-output')

    def get_busy_status(self):
        try:
            return open('/tmp/ajenti-pacman-output', 'r').read().splitlines()[-1]
        except:
            return ''

    def get_expected_result(self, st):
        r = {}

        cmd = 'pacman -Sp --noconfirm --print-format \'%n %v\' '
        a = False
        for x in st.pending:
            if st.pending[x] == 'install':
                cmd += x + ' '
                a = True
                
        if a:
            r.update(self._parse_pm_p(shell(cmd).splitlines(), 'install'))
        
        cmd = 'pacman -Rpc --noconfirm --print-format \'%n %v\' '
        a = False
        for x in st.pending:
            if st.pending[x] != 'install':
                cmd += x + ' '
                a = True
                
        if a:
            r.update(self._parse_pm_p(shell(cmd).splitlines(), 'remove'))
 
        return r

    def abort(self):
        shell('pkill pacman')
        shell('rm /tmp/ajenti-pacman-output')

    def get_info(self, pkg):
        i = apis.pkgman.PackageInfo()
        ss = shell('pacman -Qi '+pkg).split('\n')
        i.installed = ''
        i.available = ss[1].split(':')[1]
        while len(ss)>0 and not ss[0].startswith('Desc'):
            ss = ss[1:]
        ss[0] = ss[0].split(':')[1]
        i.description = '\n'.join(ss)
        return i

    def get_info_ui(self, pkg):
        pass
               
    def _save_pending(self, p):
        f = open('/tmp/ajenti-pacman-pending.list', 'w')
        for x in p:
            f.write('%s %s\n' % (p[x], x))
        f.close()

    def _parse_pm(self, ss):
        r = {}
        while len(ss)>0:
            s = ss[0].split()
            ss.pop(0)
            try:
                if '/' in s[0]:
                    s[0] = s[0].split('/')[1]
                r[s[0]] = apis.pkgman.Package()
                r[s[0]].name = s[0]
                r[s[0]].version = s[1]
                r[s[0]].description = ''
                r[s[0]].state = 'installed' if shell_status('pacman -Q '+s[0])==0 else 'removed'
                while ss[0][0] in ['\t', ' '] and len(ss)>0:
                    r[s[0]].description += ss[0]
                    ss.pop(0)
            except:
                pass
        return r

    def _parse_pm_p(self, ss, v):
        r = {}
        while len(ss)>0:
            s = ss[0].split()
            ss.pop(0)
            try:
                if '/' in s[0]:
                    s[0] = s[0].split('/')[1]
                r[s[0]] = v
                while ss[0][0] in ['\t', ' '] and len(ss)>0:
                    ss.pop(0)
            except:
                pass
        return r

    def _parse_pm_u(self, ss):
        r = {}
        for s in ss:
            s = s.split()
            try:
                if '/' in s[0]:
                    s[0] = s[0].split('/')[1]
                r[s[0]] = apis.pkgman.Package()
                r[s[0]].name = s[0]
                r[s[0]].version = s[1]
                r[s[0]].state = 'installed'
            except:
                pass
        return r

    def _get_all(self):
        ss = shell('pacman -Q').splitlines()
        return self._parse_pm_u(ss)
        
