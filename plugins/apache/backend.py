import os
import glob

from ajenti.utils import *

def is_running():
    return shell_status('pgrep apache apache2') == 0

def list_hosts():
    return [s.replace('/etc/apache2/sites-available/', '')
             for s in glob.glob('/etc/apache2/sites-available/*')]
             
def enable_host(s):
    os.symlink('/etc/apache2/sites-available/' + s, '/etc/apache2/sites-enabled/' + s)

def disable_host(s):
    os.remove('/etc/apache2/sites-enabled/' + s)

def host_enabled(s):
    return os.path.exists('/etc/apache2/sites-enabled/' + s)

def read_host_config(s):
    with open('/etc/apache2/sites-available/' + s, 'r') as f:
        return f.read()

def save_host_config(s, c):
    with open('/etc/apache2/sites-available/' + s, 'w') as f:
        f.write(c)
    
