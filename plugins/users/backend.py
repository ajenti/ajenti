from subprocess import *

from ajenti.api import *
from ajenti.utils import *


class User:
    login = ''
    uid = 0
    gid = 0
    home = ''
    shell = ''
    info = ''
    groups = []


class Group:
    name = ''
    gid = 0
    users = []


class LinuxConfig(ModuleConfig):
    plugin = 'usersbackend'
    platform = ['debian', 'arch', 'opensuse']
    
    cmd_add = 'useradd %s'
    cmd_del = 'userdel %s'
    cmd_add_group = 'groupadd %s'
    cmd_del_group = 'groupdel %s'
    cmd_set_user_login = 'usermod -l %s %s'
    cmd_set_user_uid = 'usermod -u %s %s'
    cmd_set_user_gid = 'usermod -g %s %s'
    cmd_set_user_shell = 'usermod -s %s %s'
    cmd_set_user_home = 'usermod -h %s %s'
    cmd_set_group_gname = 'groupmod -n %s %s'
    cmd_set_group_ggid = 'groupmod -g %s %s'
    cmd_add_to_group = 'adduser %s %s'
    cmd_remove_from_group = 'deluser %s %s'


class UsersBackend(Plugin):
    def __init__(self):
        self.cfg = self.app.get_config(self)
        
    def get_all_users(self):
        r = []
        for s in open('/etc/passwd', 'r').read().split('\n'):
            try:
                s = s.split(':')
                u = User()
                u.login = s[0]
                u.uid = int(s[2])
                u.gid = int(s[3])
                u.info = s[4]
                u.home = s[5]
                u.shell = s[6]
                r.append(u)
            except:
                pass
    
        sf = lambda x: -1 if x.uid==0 else (x.uid+1000 if x.uid<1000 else x.uid-1000)
        return sorted(r, key=sf)

    def get_all_groups(self):
        r = []
        for s in open('/etc/group', 'r').read().split('\n'):
            try:
                s = s.split(':')
                g = Group()
                g.name = s[0]
                g.gid = s[2]
                g.users = s[3].split(',')
                r.append(g)
            except:
                pass
    
        return r
    
    def map_groups(self, users, groups):
        for u in users:
            u.groups = []
            for g in groups:
                if u.login in g.users:
                    u.groups.append(g.name)
    
    def get_user(self, name, users):
        return filter(lambda x:x.login == name, users)[0]
    
    def get_group(self, name, groups):
        return filter(lambda x:x.name == name, groups)[0]
    
    def add_user(self, v):
        shell(self.cfg.cmd_add % v)
    
    def add_group(self, v):
        shell(self.cfg.cmd_add_group % v)
    
    def del_user(self, v):
        shell(self.cfg.cmd_del % v)
    
    def del_group(self, v):
        shell(self.cfg.cmd_del_group % v)

    def add_to_group(self, u, v):
        shell(self.cfg.cmd_add_to_group % (u,v))
    
    def remove_from_group(self, u, v):
        shell(self.cfg.cmd_remove_from_group % (u,v))
    
    def change_user_param(self, u, p, l):
        shell(getattr(self.cfg, 'cmd_set_user_'+p) % (l,u))

    def change_user_password(self, u, l):
        shell_stdin('passwd ' + u, '%s\n%s\n' % (l,l))

    def change_group_param(self, u, p, l):
        shell(getattr(self.cfg, 'cmd_set_group_'+p) % (l,u))
        shell('groupmod -n %s %s' % (l,u))

