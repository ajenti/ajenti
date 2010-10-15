import os
import subprocess
import time

from ajenti.com import *
from ajenti.app.helpers import SessionPlugin
from ajenti.ui import *
from ajenti import utils
from ajenti import apis
from ajenti.plugins.uzuri_common import *
from ajenti.misc import BackgroundWorker


def _ssh_shell(cmd):
    node = utils.ssh_node
    cmd1 = cmd
    cmd2 = ''
    if '>' in cmd:
        cmd1, cmd2 = cmd.split('>')
    return utils._shell_backup('ssh -p %s root@%s \'%s\' %s'%(node.port, node.address, cmd1, cmd2))

def _ssh_shell_status(cmd):
    node = utils.ssh_node
    cmd1 = cmd
    cmd2 = ''
    if '>' in cmd:
        cmd1, cmd2 = cmd.split('>')
    return utils._shell_st_backup('ssh -p %s root@%s \'%s\' %s'%(node.port, node.address, cmd1, cmd2))

def _ssh_shell_bg(c, output=None, deleteout=False):
    node = utils.ssh_node
    c =  'ssh -p %s root@%s \'%s\''%(node.port, node.address, c)
    if output is not None:
        c = 'bash -c "%s" > %s 2>&1'%(c,output)
        if deleteout:
            c = 'touch %s; %s; rm -f %s'%(output,c,output)
    print c
    subprocess.Popen(c, shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)    


class RemoteWorker(BackgroundWorker):
    def run(self, *args):
        res = {}
        m = args[0]
        try:
            for node in m.master.cfg.nodes:
                self.status = 'Working at %s' % node.address
                m._enable_ssh(node)
                res[node] = args[1](*args[2])
                while m.backend.is_busy():
                    time.sleep(0.5)
                m._disable_ssh()
        finally:
            m._disable_ssh()
    
    
class ClusterPackageManager(SessionPlugin):
    implements((apis.pkgman.IPackageManager, -9000))

    def __init__(self):
        SessionPlugin.__init__(self, self.app)
        try:
            self.app.config.get('clusterpkg-init')
            return
        except:
            self.app.config.set('clusterpkg-init', '1')
            
        self.master = UzuriMaster(self.app)
        self.master.load()
        self.get_backend()        
        del self.app.config.internal['clusterpkg-init']

    def get_backend(self):
        for pl in self.app.grab_plugins(apis.pkgman.IPackageManager):
            if pl.__class__ != self.__class__:
                self.backend = pl
                break
        
    def on_session_start(self):
        self._worker = None
                        
    def _enable_ssh(self, node):
        utils.ssh_node = node
        if utils.shell != _ssh_shell:
            utils._shell_backup = utils.shell
            utils._shell_st_backup = utils.shell_status
            utils._shell_bg_backup = utils.shell_bg
            utils.shell = _ssh_shell
            utils.shell_status = _ssh_shell_status
            utils.shell_bg = _ssh_shell_bg
        
    def _disable_ssh(self):
        if utils.shell == _ssh_shell:
            utils.shell = utils._shell_backup
            utils.shell_status = utils._shell_st_backup
            utils.shell_bg = utils._shell_bg_backup

    def _remote_exec(self, func, *args, **kwargs):
        res = {}
        for node in self.master.cfg.nodes:
            self._enable_ssh(node)
            res[node] = func(*args, **kwargs)
        self._disable_ssh()
        return res

    def _remote_exec_bg(self, func, *args, **kwargs):
        self._worker = RemoteWorker(func, *args)
        self._worker.start()
        
    ################        
    # Implementation
    
    def refresh(self, st):
        if not self.master.is_enabled():
            return self.backend.refresh(st)
            
        st.upgradeable = None
        st.full = None
        for node in self.master.cfg.nodes:
            self.status = node.address
            self._enable_ssh(node)
            xs = apis.pkgman.Status()
            self.backend.refresh(xs)
            if st.full is None:
                st.full = xs.full
                for k in st.full:
                    st.full[k].locations = {node: st.full[k].version}
                st.upgradeable = xs.upgradeable
            else:
                for k in xs.full.keys():
                    if not k in st.full.keys():
                        st.full[k] = xs.full[k]
                        st.full[k].locations = {node: xs.full[k].version}
                        st.full[k].state = 'broken'
                    else:
                        st.full[k].locations[node] = xs.full[k].version
                for k in st.full.keys():
                    if (not k in xs.full.keys()) or st.full[k].version != xs.full[k].version:
                        st.full[k].state = 'broken'
                for k in xs.upgradeable.keys():
                    st.upgradeable[k] = xs.upgradeable[k]

        self._disable_ssh()
        
        st.pending = {}
        try:
            ss = open('/tmp/ajenti-cluster-pending.list', 'r').read().splitlines()
            for s in ss:
                s = s.split()
                try:
                    st.pending[s[1]] = s[0]
                except:
                    pass
        except:
            pass

        self._status = st
        
        
    def get_lists(self):
        if not self.master.is_enabled():
            return self.backend.get_lists()
            
        self._remote_exec_bg(self, self.backend.get_lists, [])

    def search(self, q, st):
        if not self.master.is_enabled():
            return self.backend.search(q, st)

        res = self._remote_exec(self.backend.search, q, st)
        for k in res:
            return res[k]

    def mark_install(self, st, name):
        if not self.master.is_enabled():
            return self.backend.mark_install(st, name)

        st.pending[name] = 'install'
        self._save_pending(st.pending)

    def mark_remove(self, st, name):
        if not self.master.is_enabled():
            return self.backend.mark_remove(st, name)

        st.pending[name] = 'remove'
        self._save_pending(st.pending)

    def mark_cancel(self, st, name):
        if not self.master.is_enabled():
            return self.backend.mark_cancel(st, name)

        del st.pending[name]
        self._save_pending(st.pending)

    def mark_cancel_all(self, st):
        if not self.master.is_enabled():
            return self.backend.mark_cancel_all(st)

        st.pending = {}
        self._save_pending(st.pending)
    
    def apply(self, st):
        if not self.master.is_enabled():
            return self.backend.apply(st)
        self._remote_exec_bg(self, self.backend.apply, [st])

    def is_busy(self):
        if not self.master.is_enabled():
            return self.backend.is_busy()
        return self._worker is not None and self._worker.alive

    def get_busy_status(self):
        if not self.master.is_enabled():
            return self.backend.get_busy_status()

        try:
            return self._worker.status
        except:
            return ''

    def get_expected_result(self, st):
        if not self.master.is_enabled():
            return self.backend.get_expected_result(st)
        return st.pending

    def abort(self):
        if not self.master.is_enabled():
            return self.backend.abort()
        self._remote_exec(self.backend.abort)
        
    def get_info(self, pkg):
        if not self.master.is_enabled():
            return self.backend.get_info(pkg)
        res = self._remote_exec(self.backend.get_info, pkg)
        for k in res:
            return res[k]
        
    def get_info_ui(self, pkg):
        if not self.master.is_enabled():
            return self.backend.get_info_ui(pkg)

        t = UI.DataTable(
                UI.DataTableRow(
                    UI.DataTableCell(
                        width=20
                    ),
                    UI.Label(text='Node'),
                    UI.Label(text='Version'),
                    header=True
                )
            )
        for node in self.master.cfg.nodes:
            p = self._status.full[pkg]
            print p.locations
            r = UI.DataTableRow(
                        UI.Image(file='/dl/pkgman/package-available.png'),
                        UI.Label(text='%s (%s)'%(node.desc,node.address)),
                        UI.Label(text='not installed')
                    )
            for n in p.locations:
                if n.address == node.address:
                    r = UI.DataTableRow(
                            UI.Image(file='/dl/pkgman/package-installed.png'),
                            UI.Label(text='%s (%s)'%(node.desc,node.address)),
                            UI.Label(text=p.locations[n])
                        )
            t.append(r)
        return UI.VContainer(UI.Label(text='Cluster status', size=3), t)
        
    def _save_pending(self, p):
        f = open('/tmp/ajenti-cluster-pending.list', 'w')
        for x in p:
            f.write('%s %s\n' % (p[x], x))
        f.close()
