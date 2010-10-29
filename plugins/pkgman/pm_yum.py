import os
import subprocess

from ajenti.com import *
from ajenti import utils
from ajenti import apis


class YumPackageManager(Plugin):
    implements(apis.pkgman.IPackageManager)
    platform = ['centos', 'fedora']

    _pending = {}

    def refresh(self, st):
        p = self._parse_yum(utils.shell('yum -C -q check-update').splitlines())
        a = self._get_all()
        st.upgradeable = {}

        for s in p:
            s = p[s]
            if s.state == 'installed':
            	if a.has_key(s.name) and a[s.name].state == 'installed':
                    st.upgradeable[s.name] = a[s.name]

        st.pending = {}
        try:
            ss = open('/tmp/ajenti-yum-pending.list', 'r').read().splitlines()
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
        utils.shell_bg('yum check-update', output='/tmp/ajenti-yum-output', deleteout=True)

    def search(self, q, st):
        ss = utils.shell('yum -q -C search %s' % q).splitlines()
        a = st.full
        r = {}
        for s in ss:
            s = s.split()
	    if s[0].startswith('===='):
	        continue
	    else:
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

    def mark_cancel_all(self, st):
        st.pending = {}
        self._save_pending(st.pending)
    
    def apply(self, st):
        cmd = 'yum -y install '
        for x in st.pending:
            cmd += x + (' ' if st.pending[x] == 'install' else ' ')
        utils.shell_bg(cmd, output='/tmp/ajenti-yum-output', deleteout=True)

    def is_busy(self):
        if utils.shell_status('ps ax | grep \"/usr/bin/python /usr/bin/yum\" | grep -v \"grep /usr/bin/python /usr/bin/yum\" | awk \'{print $1}\'') != 0: return False
        return os.path.exists('/tmp/ajenti-yum-output')

    def get_busy_status(self):
        try:
            return open('/tmp/ajenti-yum-output', 'r').read().splitlines()[-1]
        except:
            return ''

    def get_expected_result(self, st):
        return st.pending

    def abort(self):
        utils.shell('killall -9 yum')
        utils.shell('rm /tmp/ajenti-yum-output')

    def get_info(self, pkg):
        pass #do it later       
	 
    def get_info_ui(self, pkg):
        return None

    def _save_pending(self, p):
        f = open('/tmp/ajenti-yum-pending.list', 'w')
        for x in p:
            f.write('%s %s\n' % (p[x], x))
        f.close()

    def _parse_yum(self, ss):
        r = {}
        for s in ss:
            s = s.split()
            try:
                if s[0] == '':
                    continue
                else:
		    r[s[0]] = apis.pkgman.Package()
                    r[s[0]].name = s[0]
                    r[s[0]].version = s[1]
                    r[s[0]].state = 'installed'
            except:
                pass
	return r

    def _get_all(self):
        ss = utils.shell('yum -C list installed -q').splitlines()
        r = {}
        for s in ss:
            s = s.split()
            try:
                p = apis.pkgman.Package()
                p.name = s[0]
                p.version = s[1]
                p.state = 'installed'
                r[p.name] = p
            except:
                pass

        return r

