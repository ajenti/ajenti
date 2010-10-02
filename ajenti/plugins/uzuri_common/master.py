import os
import time
import tempfile
import shutil
import re

from ajenti.com import Plugin
from ajenti.utils import shell

from api import IClusteredConfig


class UzuriMaster(Plugin):
    config_dir = '/var/spool/uzuri'

    def __init__(self):
        try:
            self.is_enabled()
        except:
            self.disable()
        
    def load(self):
        self.cfg = Config()
        #self.deploy_node(self.cfg.nodes[0])
        
    def is_installed(self):
        return os.path.exists(self.config_dir)
    
    def is_enabled(self):
        return self.config.get('uzuri-root') == self.config_dir

    def get_current_timestamp(self):
        return os.getmtime(self.config_dir)
        
    def install(self):
        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)
        cfgs = self.app.grab_plugins(IClusteredConfig)
        for cfg in cfgs:
            self.copy_current_config(cfg)
     
    def copy_current_config(self, cfg):
        for f,m in cfg.files:
            shell('mkdir -p ' + self.config_dir + f)
            shell('rm -r %s%s/%s' % (self.config_dir,f,m))
            shell('cp -r %s/%s %s%s/' % (f,m,self.config_dir,f))
            
    def enable(self):
        self.config.set('uzuri-root', self.config_dir)
        
    def disable(self):
        self.config.set('uzuri-root', '')


    def deploy_node(self, node):
        cfgs = self.app.grab_plugins(IClusteredConfig)
        for cfg in cfgs:
            self.deploy_config(cfg, node)
                
    def deploy_config(self, cfg, node):
        tmp = tempfile.mkdtemp()
        for f,m in cfg.files:
            path = tmp + f
            shell('mkdir -p ' + path)
            shell('cp -r %s%s/%s %s' % (self.config_dir,f,m,path))
            for root, dirs, files in os.walk(path):
                for fl in files:
                    self._insert_vars(os.path.join(root, fl), node)
                    
            self._ssh_run(node, 'rm -r %s/%s'%(f,m))
        self._ssh_copy('%s/*'%tmp, node, '/')
        shutil.rmtree(tmp)    
    
    def _ssh_copy(self, src, node, dst):
        shell('scp -pBr -P %s %s root@%s:%s'%(node.port, src, node.address, dst))

    def _ssh_run(self, node, cmd):
        shell('ssh -p %s root@%s %s'%(node.port, node.address, cmd))
    
    def _insert_vars(self, file, node):
        d = open(file, 'r').read()
        for k in node.vars:
            d = re.sub('{u:%s}'%k, node.vars[k], d)
        open(file, 'w').write(d)
        
        
class Config:
    config_file = '/etc/ajenti/uzuri.conf'

    def __init__(self):
        self.nodes = []
        self.vars = []
        if not os.path.exists(self.config_file):
            return
        ll = open(self.config_file).read().split('\n')
        for l in ll:
            if l != '':
                if l.startswith('host'):
                    n = ClusterNode()
                    tmp, n.address, n.port, n.password, n.timestamp, v = l.split(':')
                    v = [x.split('=') for x in v.split(';')]
                    for x in v:
                        n.vars[x[0]] = x[1]
                    self.nodes.append(n)
                elif l.startswith('var'):
                    self.vars.append(l.split(':')[1])
                    
        self.nodes = sorted(self.nodes, key=lambda x:x.address)
        self.vars = sorted(self.vars)

    def save(self):
        d = ''
        for n in self.vars:
            d += 'var:%s\n'%n
        for n in self.nodes:
            v = ';'.join(['%s=%s'%(x,n.vars[x]) for x in n.vars.keys()])
            d += 'node:%s:%s:%s:%s:%s\n' % (n.address,n.port,n.password,n.timestamp,v)
        open(self.config_file, 'w').write(d)        
        
        
class ClusterNode:
    def __init__(self):
        self.address = ''
        self.port = '22'
        self.password = ''
        self.timestamp = '0'
        self.vars = {}
        
