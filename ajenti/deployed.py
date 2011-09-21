import os
from ajenti.utils import hash_pw, shell
from ConfigParser import ConfigParser


RCFG_FILE = '/root/ajenti-re.conf'

def reconfigure(cfg): 
    if not os.path.exists(RFCG_FILE):
        return
        
    rcfg = ConfigParser()
    rcfg.load(RCFG_FILE)
    
    if rcfg.has_option('ajenti', 'credentials'):
        u,p = rcfg.get('ajenti', 'credentials').split(':')
        cfg.remove_option('users', 'admin')
        if not p.startswith('{SHA}'):
            p = hash_pw(p)
        cfg.set('users', u, p)
        
    if rcfg.has_option('ajenti', 'plugins'):
        for x in rcfg.get('ajenti', 'plugins').split():
            shell('ajenti-pkg get ' + x)

    if rcfg.has_option('ajenti', 'ssl'):
        c,k = rcfg.get('ajenti', 'ssl').split()
        cfg.set('ssl', '1')
        cfg.set('cert_key', k)
        cfg.set('cert_file', c)

    if rcfg.has_option('ajenti', 'port'):
        cfg.set('ajenti', 'bind_port', rcfg.get('ajenti', 'port'))

    if rcfg.has_option('ajenti', 'host'):
        cfg.set('ajenti', 'bind_host', rcfg.get('ajenti', 'host'))

    cfg.set('ajenti', 'firstrun', 'no')
    cfg.save()
    #os.unlink(RCFG_FILE)
