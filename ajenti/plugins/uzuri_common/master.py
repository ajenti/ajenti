import os
import time
import tempfile
import shutil
import re

from ajenti.com import Plugin
from ajenti.utils import shell
from ajenti.misc import BackgroundWorker

from api import IClusteredConfig


class UzuriMaster(Plugin):
    config_dir = '/var/spool/uzuri'
    worker = None
    
    def __init__(self):
        try:
            self.is_enabled()
        except:
            self.config.set('uzuri-root', '')
        
    def load(self):
        self.cfg = Config()
        
    def is_installed(self):
        return os.path.exists(self.config_dir)
    
    def is_enabled(self):
        return self.config.get('uzuri-root') == self.config_dir

    def is_busy(self):
        if self.worker is None:
            return False
        if not self.worker.is_running():
            self.worker = None
            return False
        return True        
            
    def get_parts(self):
        return self.app.grab_plugins(IClusteredConfig)
            
    def install(self):
        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)
        cfgs = self.get_parts()
        for cfg in cfgs:
            self.copy_current_config(cfg)
     
    def copy_current_config(self, cfg):
        for f,m in cfg.files:
            shell('mkdir -p ' + self.config_dir + f)
            shell('rm -r %s%s/%s' % (self.config_dir,f,m))
            shell('cp -r %s/%s %s%s/' % (f,m,self.config_dir,f))
            
    def enable(self):
        self.config.set('uzuri-root', self.config_dir)
        self.app.session.clear()
        
    def disable(self):
        self.config.set('uzuri-root', '')
        self.app.session.clear()


    def deploy_all(self):
        if self.is_busy():
            return 
        self.worker = DeploymentWorker(self, *self.cfg.nodes)
        self.worker.start()

    def deploy_node(self, node):
        if self.is_busy():
            return 
        self.worker = DeploymentWorker(self, node)
        self.worker.start()
            
    def deploy_node_synced(self, node):
        cfgs = self.get_parts()
        for cfg in cfgs:
            if cfg.id in self.cfg.parts:
                self.deploy_config(cfg, node)
        node.timestamp = str(int(time.time()))
        self.cfg.save()
        
    def deploy_config(self, cfg, node):
        tmp = tempfile.mkdtemp()
        for f,m in cfg.files:
            path = tmp + f
            shell('mkdir -p ' + path)
            shell('cp -r %s%s/%s %s' % (self.config_dir,f,m,path))
            for root, dirs, files in os.walk(path):
                for fl in files:
                    try:
                        self._insert_vars(os.path.join(root, fl), node)
                    except:
                        pass
                    
            self._ssh_run(node, 'rm -r %s/%s'%(f,m))
        self._ssh_copy('%s/*'%tmp, node, '/')
        shutil.rmtree(tmp)    
        
        _rt = self.config.get('uzuri-root')
        self.config.set('uzuri-root', self.config_dir)
        for cmd in cfg.run_after:
            self._ssh_run(node, self._insert_vars_str(cmd, node))
        self.config.set('uzuri-root', _rt)
            
    
    def _ssh_copy(self, src, node, dst):
        shell('scp -pBr -P %s %s root@%s:%s'%(node.port, src, node.address, dst))

    def _ssh_run(self, node, cmd):
        shell('ssh -p %s root@%s \'%s\''%(node.port, node.address, cmd))
    
    def _insert_vars(self, file, node):
        d = open(file, 'r').read()
        open(file, 'w').write(self._insert_vars_str(d, node))

    def _insert_vars_str(self, d, node):
        for k in node.vars:
            d = re.sub('{u:%s}'%k, node.vars[k], d)
        return d
        
        
class DeploymentWorker(BackgroundWorker):
    status = ''
    
    def run(self, *args):
        if len(args) == 1: return
        for node in args[1:]:
            self.status = node.address
            args[0].deploy_node_synced(node)
        
    
class Config:
    config_file = '/etc/ajenti/uzuri.conf'

    def __init__(self):
        self.nodes = []
        self.vars = []
        self.parts = []
        
        if not os.path.exists(self.config_file):
            return
        ll = open(self.config_file).read().split('\n')
        for l in ll:
            if l != '':
                if l.startswith('node'):
                    n = ClusterNode()
                    tmp, n.desc, n.address, n.port, n.timestamp, v = l.split(':')
                    v = [x.split('=') for x in v.split(';')]
                    for x in v:
                        n.vars[x[0]] = x[1]
                    self.nodes.append(n)
                elif l.startswith('var'):
                    self.vars.append(l.split(':')[1])
                elif l.startswith('part'):
                    self.parts.append(l.split(':')[1])
                    
        self.nodes = sorted(self.nodes, key=lambda x:x.address)
        self.vars = sorted(self.vars)

    def save(self):
        d = ''
        for n in self.parts:
            d += 'part:%s\n'%n
        for n in self.vars:
            d += 'var:%s\n'%n
        for n in self.nodes:
            v = ';'.join(['%s=%s'%(x,n.vars[x]) for x in n.vars.keys()])
            d += 'node:%s:%s:%s:%s:%s\n' % (n.desc,n.address,n.port,n.timestamp,v)
        open(self.config_file, 'w').write(d)        
        
        
class ClusterNode:
    def __init__(self):
        self.desc = ''
        self.address = ''
        self.port = '22'
        self.timestamp = '0'
        self.vars = {}
        
