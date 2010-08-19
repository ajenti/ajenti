import os
import subprocess

from ajenti.com import *
from ajenti.utils import *
from ajenti import apis


class APTPackageManager(Plugin):
    implements(apis.pkgman.IPackageManager)
    platform = ['Debian', 'Ubuntu']

    _pending = {}

    def refresh(self, st):
        p = self._parse_apt(shell('apt-get upgrade -s -qq').splitlines())
        a = self._get_all()
        st.upgradeable = {}

        for s in p:
            s = p[s]
            if s.action == 'installed':
                if a.has_key(s.name) and a[s.name].state == 'installed':
                    st.upgradeable[s.name] = a[s.name]

        st.pending = {}
        try:
            ss = open('/tmp/ajenti-apt-pending.list', 'r').read().splitlines()
            for s in ss:
                s = s.split()
                try:
                    st.pending[s[1]] = s[0]
                except:
                    pass
        except:
            pass

        st.list = a

    def get_lists(self):
        cmd = 'apt-get update > /tmp/ajenti-apt-output; rm -f /tmp/ajenti-apt-output &'
        subprocess.Popen(['bash', '-c', cmd])

    def search(self, q):
        ss = shell('apt-cache search %s' % q).splitlines()
        a = self._get_all()
        r = {}
        for s in ss:
            s = s.split()
            r[s[0]] = apis.pkgman.Package()
            r[s[0]].name = s[0]
            r[s[0]].description = ' '.join(s[2:])
            r[s[0]].state = 'removed'
            if a.has_key(s[0]) and a[s[0]].state == 'installed':
                r[s[0]].state = 'installed'
        return r

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
        cmd = 'apt-get -y install '
        for x in st.pending:
            cmd += x + ('+ ' if st.pending[x] == 'install' else '- ')
        cmd += ' > /tmp/ajenti-apt-output; rm -f /tmp/ajenti-apt-output &'
        subprocess.Popen(['bash', '-c', cmd])

    def is_busy(self):
        if shell_status('pgrep apt-get') != 0: return False
        return os.path.exists('/tmp/ajenti-apt-output')

    def get_busy_status(self):
        try:
            return open('/tmp/ajenti-apt-output', 'r').read().splitlines()[-1]
        except:
            return ''

    def get_expected_result(self, st):
        cmd = 'apt-get -qq -s install '
        for x in st.pending:
            cmd += x + ('+ ' if st.pending[x] == 'install' else '- ')
        r = self._parse_apt(shell(cmd).splitlines())
        for x in r:
            if r[x].action == 'installed':
                r[x] = 'install'
            else:
                r[x] = 'remove'
        return r

    def _save_pending(self, p):
        f = open('/tmp/ajenti-apt-pending.list', 'w')
        for x in p:
            f.write('%s %s\n' % (p[x], x))
        f.close()

    def _parse_apt(self, ss):
        r = {}
        for s in ss:
            s = s.split()
            try:
                if s[0] == 'Inst':
                    r[s[1]] = apis.pkgman.Package()
                    r[s[1]].name = s[1]
                    r[s[1]].version = s[2].strip('[]')
                    r[s[1]].action = 'installed'
                if s[0] == 'Purg':
                    r[s[1]] = apis.pkgman.Package()
                    r[s[1]].name = s[1]
                    r[s[1]].version = s[2].strip('[]')
                    r[s[1]].action = 'removed'
            except:
                pass
        return r

    def _get_all(self):
        ss = shell('dpkg -l').splitlines()
        r = {}
        for s in ss:
            s = s.split()
            try:
                p = apis.pkgman.Package()
                p.name = s[1]
                p.version = s[2]
                if s[0][1] == 'i':
                    p.state = 'installed'
                else:
                    p.state = 'removed'
                r[p.name] = p
            except:
                pass

        return r
