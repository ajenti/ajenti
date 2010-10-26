import os
import subprocess

from ajenti.com import *
from ajenti import utils
from ajenti import apis


class ZypperPackageManager(Plugin):
    implements(apis.pkgman.IPackageManager)
    platform = ['opensuse']

    _pending = {}

    def refresh(self, st):
        a = self._get_all()
        st.upgradeable = self._parse_zypp_lu(utils.shell('zypper -An list-updates').splitlines())

        st.pending = {}
        try:
            ss = open('/tmp/ajenti-zypper-pending.list', 'r').read().splitlines()
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
        utils.shell_bg('zypper ref', output='/tmp/ajenti-zypp-output', deleteout=True)

    def search(self, q, st):
        return self._parse_zypp(utils.shell('zypper -An search %s' % q).splitlines())

    def mark_install(self, st, name):
        st.pending[name] = 'install'
        self._save_pending(st.pending)

    def mark_remove(self, st, name):
        st.pending[name] = 'remove'
        self._save_pending(st.pending)

    def mark_cancel(self, st, name):
        del st.pending[name]
        self._save_pending(st.pending)

    def mark_cancel_all(self, st):
        st.pending = {}
        self._save_pending(st.pending)
    
    def apply(self, st):
        cmd = 'zypper -n install ' #!
        for x in st.pending:
            cmd += (' ' if st.pending[x] == 'install' else ' -') + x
        utils.shell_bg(cmd, output='/tmp/ajenti-zypper-output', deleteout=True)

    def is_busy(self):
        if utils.shell_status('pgrep zypper') != 0: return False
        return os.path.exists('/tmp/ajenti-zypper-output')

    def get_busy_status(self):
        try:
            return open('/tmp/ajenti-zypper-output', 'r').read().splitlines()[-1]
        except:
            return ''

    def get_expected_result(self, st):
        return st.pending

    def abort(self):
        utils.shell('pkill zypper')
        utils.shell('rm /tmp/ajenti-zypper-output')
        
    def get_info(self, pkg):
        return apis.pkgman.PackageInfo() # TODO: I've f#cked up my Suse VM so please add info parser here

    def get_info_ui(self, pkg):
        pass

    def _save_pending(self, p):
        f = open('/tmp/ajenti-zypper-pending.list', 'w')
        for x in p:
            f.write('%s %s\n' % (p[x], x))
        f.close()

    def _parse_zypp(self, ss):
        r = {}
        
        for s in ss:
            s = [x.strip() for x in s.split('|')]
            try:
                r[s[1]] = apis.pkgman.Package()
                r[s[1]].name = s[1]
                r[s[1]].version = ''
                r[s[1]].description = s[2]
                if s[0] == 'i':
                    r[s[1]].state = 'installed'
                else:
                    r[s[1]].state = 'removed'
            except:
                pass
        return r

    def _parse_zypp_lu(self, ss):
        r = {}
        for s in ss:
            s = [x.strip() for x in s.split('|')]
            try:
                if s[2] == 'Name':
                    continue
                r[s[2]] = apis.pkgman.Package()
                r[s[2]].name = s[2]
                r[s[2]].version = s[3]
                r[s[2]].state = 'installed'
            except:
                pass
        return r

    def _get_all(self):
        ss = utils.shell('zypper -An search \'*\'').splitlines()
        return self._parse_zypp(ss)
