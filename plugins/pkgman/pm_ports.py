import os
import subprocess

from ajenti.com import *
from ajenti import utils
from ajenti import apis


class PortsPackageManager(Plugin):
    implements(apis.pkgman.IPackageManager)
    platform = ['freebsd']

    _pending = {}

    def refresh(self, st):
        p = utils.shell('pkg_version|grep \'<\'').split('\n')
        a = self._get_all()
        st.upgradeable = {}

        for x in p:
            try:
                s = x.split()[0]
                st.upgradeable[s] = a[s]
            except:
                pass
                
        st.pending = {}
        try:
            ss = open('/tmp/ajenti-ports-pending.list', 'r').read().splitlines()
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
        utils.shell_bg('portsnap fetch', output='/tmp/ajenti-ports-output', deleteout=True)

    def search(self, q, st):
        ss = utils.shell('cd /usr/ports; make search name=%s' % q).splitlines()
        a = st.full
        r = {}
        while len(ss)>0:
            if ss[0].startswith('Port'):
                pkg = apis.pkgman.Package()            
                pkg.name = ss[0].split()[1].split('-')[0]
                pkg.state = 'removed'
                if a.has_key(pkg.name) and a[pkg.name].state == 'installed':
                    pkg.state = 'installed'
                r[pkg.name] = pkg
            if ss[0].startswith('Info'):
                pkg.description = ' '.join(ss[0].split()[1:])
            ss = ss[1:]
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

    def mark_cancel_all(self, st):
        st.pending = {}
        self._save_pending(st.pending)
    
    def apply(self, st):
        cmd = 'portupgrade -R'
        cmd2 = 'pkg_deinstall -r'
        for x in st.pending:
            if st.pending[x] == 'install':
                cmd += ' ' + x
            else:
                cmd2 += ' ' + x
        utils.shell_bg('%s; %s'%(cmd,cmd2), output='/tmp/ajenti-ports-output', deleteout=True)

    def is_busy(self):
        return os.path.exists('/tmp/ajenti-ports-output')

    def get_busy_status(self):
        try:
            return open('/tmp/ajenti-ports-output', 'r').read().splitlines()[-1]
        except:
            return ''

    def get_expected_result(self, st):
        cmd = 'portupgrade -Rn'
        cmd2 = 'pkg_deinstall -nr'
        for x in st.pending:
            if st.pending[x] == 'install':
                cmd += ' ' + x
            else:
                cmd2 += ' ' + x

        r = utils.shell('%s; %s | grep \'[+-] \''%(cmd,cmd2)).splitlines()
        res = {}
        for x in r:
            s = x.split()
            if not s[0] in ['+', '-']:
                continue
            name = '-'.join(s[-1].split('-')[:-1])[1:]
            if s[0] == '+':
                res[name] = 'install'
            else:
                res[name] = 'remove'
        return res

    def abort(self):
        utils.shell('pkill make')
        utils.shell('rm /tmp/ajenti-ports-output')
        
    def get_info(self, pkg):
        i = apis.pkgman.PackageInfo()
        ss = utils.shell('pkg_info \'%s-*\''%pkg).split('\n')
        i.installed = ''
        i.available = ss[0].split('-')[-1][:-1]
        while len(ss)>0 and not ss[0].startswith('Desc'):
            ss = ss[1:]
        ss = ss[1:]
        i.description = '\n'.join(ss)
        return i
        
    def get_info_ui(self, pkg):
        return None

    def _save_pending(self, p):
        f = open('/tmp/ajenti-ports-pending.list', 'w')
        for x in p:
            f.write('%s %s\n' % (p[x], x))
        f.close()

    def _get_all(self):
        ss = utils.shell('pkg_info').splitlines()
        r = {}
        for s in ss:
            s = s.split()
            try:
                p = apis.pkgman.Package()
                nv = s[0].split('-')
                p.name = '-'.join(nv[0:-1])
                p.version = nv[-1]
                p.description = ' '.join(s[1:])
                p.state = 'installed'
                r[p.name] = p
            except:
                pass

        return r
        
