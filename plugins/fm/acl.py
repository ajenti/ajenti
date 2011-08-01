from ajenti.utils import *

def get_acls(f):
    ss = shell('getfacl -cp -- "%s"' % f).split('\n')
    r = []
    for s in ss:
        if not s.startswith('#') and not s.startswith('getfacl'):
            try:
                x = [z.strip() for z in s.split(':')]
                x[-1] = x[-1].split()[0]
                r.append((':'.join(x[:-1]), x[-1]))
            except:
                pass
    return r
    
def del_acl(f, acl):
    print shell('setfacl -x %s "%s"'%(acl,f))

def set_acl(f, who, rights):
    print shell('setfacl -m %s:%s "%s"'%(who,rights,f))    
