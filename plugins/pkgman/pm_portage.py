import os
import subprocess
import lxml.etree

from ajenti.com import *
from ajenti.utils import shell, shell_bg
from ajenti import apis


class PortagePackageManager(Plugin):
    implements(apis.pkgman.IPackageManager)
    platform = ['gentoo']
    _pending = {}

    def refresh(self, st):
        st.full = self.eix_parse(shell('eix \'-I*\' --xml'))
        st.upgradeable = self.eix_parse(shell('eix -u --xml'))
        st.pending = self._pending

    def get_lists(self):
        utils.shell_bg('emerge --sync', output='/tmp/ajenti-portage-output', deleteout=True)

    def search(self, q, st):
        return self.eix_parse(shell('eix --xml \'%s\''%q))

    def mark_install(self, st, name):
        st.pending[name] = 'install'

    def mark_remove(self, st, name):
        st.pending[name] = 'remove'

    def mark_cancel(self, st, name):
        del st.pending[name]

    def mark_cancel_all(self, st):
        st.pending = {}

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
        return os.path.exists('/tmp/ajenti-portage-output')

    def get_busy_status(self):
        try:
            return open('/tmp/ajenti-portage-output', 'r').read().splitlines()[-1]
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
        utils.shell('pkill emerge')
        utils.shell('rm /tmp/ajenti-portage-output')

    def get_info(self, pkg):
        return self.eix_parse(shell('eix \'-I*\' --xml'))[pkg]

    def get_info_ui(self, pkg):
        return None

    def eix_parse(self, data):
        xml = lxml.etree.fromstring(data)
        r = {}

        for pkg in xml.findall('*/package'):
            try:
                p = apis.pkgman.Package()
                p.name = pkg.get('name')
                p.available = pkg.findall('version')[-1].get('id')
                if len(pkg.findall('version[@installed]')) == 0:
                    p.state = 'removed'
                else:
                    p.installed = pkg.findall('version[@installed]')[0].get('id')
                    p.version = p.installed
                p.description = pkg.find('description').text
                r[p.name] = p
            except:
                pass

        return r
