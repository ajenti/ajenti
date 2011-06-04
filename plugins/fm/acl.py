from ajenti.utils import *

def get_acls(f):
    ss = shell('getfacl "%s"' % f).split('\n')
    r = []
    for s in ss:
        if not s.startswith('#'):
            try:
                x = s.split(':')
                r.append((x[0]+':'+x[1], x[2].split(' ')[0]))
            except:
                pass
    return r
    
def del_acl(f, acl):
    print shell('setfacl -x %s "%s"'%(acl,f))

def set_acl(f, who, rights):
    print shell('setfacl -m %s:%s "%s"'%(who,rights,f))    
