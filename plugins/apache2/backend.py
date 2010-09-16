import os
import glob

from ajenti.utils import *


dir_apache = '/etc/apache2/'
dir_sites_avail = dir_apache + 'sites-available/'
dir_sites_enabled = dir_apache + 'sites-enabled/'
dir_mods_avail = dir_apache + 'mods-available/'
dir_mods_enabled = dir_apache + 'mods-enabled/'

def is_installed():
    return os.path.exists(dir_apache)
    
def is_running():
    return shell_status('pgrep apache2') == 0

# Hosts

def list_hosts():
    return sorted([s.replace(dir_sites_avail, '')
             for s in glob.glob(dir_sites_avail + '*')])
             
def enable_host(s):
    os.symlink(dir_sites_avail + s, dir_sites_enabled + s)

def disable_host(s):
    os.remove(dir_sites_enabled + s)

def host_enabled(s):
    return os.path.exists(dir_sites_enabled + s)

def read_host_config(s):
    with open(dir_sites_avail + s, 'r') as f:
        return f.read()

def save_host_config(s, c):
    with open(dir_sites_avail + s, 'w') as f:
        f.write(c)
    
# Modules

def list_modules():
    return sorted([s.replace(dir_mods_avail, '').replace('.load', '') 
             for s in glob.glob(dir_mods_avail + '*.load')])

def module_has_config(s):
    return os.path.exists(dir_mods_avail + s + '.conf')
    		
def enable_module(s):
    os.symlink(dir_mods_avail + s + '.load', dir_mods_enabled + s + '.load')
    if module_has_config(s):
        os.symlink(dir_mods_avail + s + '.conf', dir_mods_enabled + s + '.conf')

def disable_module(s):
    os.remove(dir_mods_enabled + s + '.load')
    if module_has_config(s):
        os.remove(dir_mods_enabled + s + '.conf')

def module_enabled(s):
    return os.path.exists(dir_mods_enabled + s + '.load')
    
def read_module_config(s):
    with open(dir_mods_avail + s + '.conf', 'r') as f:
        return f.read()

def save_host_config(s, c):
    with open(dir_mods_avail + s + '.conf', 'w') as f:
        f.write(c)

