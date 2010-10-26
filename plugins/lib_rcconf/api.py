from ajenti.com import *
from ajenti.apis import API
from ajenti import apis
from ajenti.utils import shell_status, shell
from ajenti.plugins.uzuri_common import ClusteredConfig
from ajenti.plugins.recovery import *


class RCConf(API):
    class RCConf(ClusteredConfig):
        platform = ['arch', 'freebsd']
        name = 'rc.conf'
        id = 'rcconf'
        files = [('/etc', 'rc.conf')] 

        def has_param(self, param):
            return shell_status('grep \'%s=\' /etc/rc.conf'%param) == 0
            
        def get_param(self, param):
            try:
                s = shell('grep \'^%s=\' /etc/rc.conf'%param).split('=')[1].strip()
            except:
                s = ''
            return s.strip('"')

        def has_param(self, param):
            return shell_status('grep \'^%s=\' /etc/rc.conf'%param) == 0

        def set_param(self, param, value, near=None):
            d = open('/etc/rc.conf').read().split('\n')
            f = open('/etc/rc.conf', 'w')
            done = False
            for s in d:
                if (not done) and (near is not None) and s.startswith(near):
                    if param is not None:
                        f.write('%s="%s"\n'%(param,value))
                    done = True
                if not (('=' in s) and s.split('=')[0].strip() == param):
                    f.write(s + '\n')
            if not done and param is not None: 
                f.write('%s="%s"\n'%(param,value))
            f.close()        


class RCConfRecovery(SimpleFileRecoveryProvider):
    name = 'rc.conf'
    id = 'rcconf'
    path = '/etc/rc.conf'
