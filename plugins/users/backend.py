from subprocess import *
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
        
def get_all_users():
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
    
    
def get_all_groups():
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
        
def map_groups(users, groups):
    for u in users:
        u.groups = []
        for g in groups:
            if u.login in g.users:
                u.groups.append(g.name)
                
def get_user(name, users):
    return filter(lambda x:x.login == name, users)[0]

def get_group(name, groups):
    return filter(lambda x:x.name == name, groups)[0]

def add_user(v):
    shell('useradd ' + v)
    
def add_group(v):
    shell('groupadd ' + v)

def del_user(v):
    shell('userdel ' + v)
    
def del_group(v):
    shell('groupdel ' + v)

def change_user_login(u, l):
    shell('usermod -l %s %s' % (l,u))
 
def change_user_uid(u, l):
    shell('usermod -u %s %s' % (l,u))

def change_user_gid(u, l):
    shell('usermod -g %s %s' % (l,u))

def change_user_shell(u, l):
    shell('usermod -s %s %s' % (l,u))

def change_user_home(u, l):
    shell('usermod -d %s %s' % (l,u))

def change_user_password(u, l):
    p = Popen(['passwd', u], stdin=PIPE)
    p.stdin.write('%s\n%s\n' % (l,l))

def change_group_name(u, l):
    shell('groupmod -n %s %s' % (l,u))

def change_group_gid(u, l):
    shell('groupmod -g %s %s' % (l,u))

