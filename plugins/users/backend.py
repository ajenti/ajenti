from subprocess import *

from ajenti.api import *
from ajenti.com import *
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


class UsersBackend(Plugin):
    icon = '/dl/users/icon.png'

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
        shell(self.cfg.cmd_add.format(v))

    def add_group(self, v):
        shell(self.cfg.cmd_add_group.format(v))

    def del_user(self, v):
        shell(self.cfg.cmd_del.format(v))

    def del_group(self, v):
        shell(self.cfg.cmd_del_group.format(v))

    def add_to_group(self, u, v):
        shell(self.cfg.cmd_add_to_group.format(u,v))

    def remove_from_group(self, u, v):
        shell(self.cfg.cmd_remove_from_group.format(u,v))

    def change_user_param(self, u, p, l):
        shell(getattr(self.cfg, 'cmd_set_user_'+p).format(l,u))

    def change_user_password(self, u, l):
        shell_stdin('passwd ' + u, '%s\n%s\n' % (l,l))

    def change_group_param(self, u, p, l):
        shell(getattr(self.cfg, 'cmd_set_group_'+p).format(l,u))


class LinuxConfig(ModuleConfig):
    target = UsersBackend
    platform = ['debian', 'arch', 'fedora', 'centos', 'gentoo']

    cmd_add = 'useradd {0}'
    cmd_del = 'userdel {0}'
    cmd_add_group = 'groupadd {0}'
    cmd_del_group = 'groupdel {0}'
    cmd_set_user_login = 'usermod -l {0} {1}'
    cmd_set_user_uid = 'usermod -u {0} {1}'
    cmd_set_user_gid = 'usermod -g {0} {1}'
    cmd_set_user_shell = 'usermod -s {0} {1}'
    cmd_set_user_home = 'usermod -h {0} {1}'
    cmd_set_group_gname = 'groupmod -n {0} {1}'
    cmd_set_group_ggid = 'groupmod -g {0} {1}'
    cmd_add_to_group = 'adduser {0} {1}'
    cmd_remove_from_group = 'deluser {0} {1}'


class BSDConfig(ModuleConfig):
    target = UsersBackend
    platform = ['freebsd']

    cmd_add = 'pw useradd {0}'
    cmd_del = 'pw userdel {0}'
    cmd_add_group = 'pw groupadd {0}'
    cmd_del_group = 'pw groupdel {0}'
    cmd_set_user_login = 'pw usermod {1} -l {0}'
    cmd_set_user_uid = 'pw usermod {1} -u {0}'
    cmd_set_user_gid = 'pw usermod {1} -g {0}'
    cmd_set_user_shell = 'pw usermod {1} -s {0}'
    cmd_set_user_home = 'pw usermod {1} -h {0}'
    cmd_set_group_gname = 'pw groupmod {1} -n {0}'
    cmd_set_group_ggid = 'pw groupmod {1} -g {0}'
    cmd_add_to_group = 'pw groupmod {1} -m {0}'
    cmd_remove_from_group = 'pw groupmod {1} -d {0}'
