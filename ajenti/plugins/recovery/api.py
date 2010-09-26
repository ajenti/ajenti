import os
import tempfile
import shutil

from ajenti.com import *
from ajenti.utils import shell_status


class IRecoveryProvider(Interface):
    name = ''
    id = ''
    

class RecoveryProvider(Plugin):
    implements(IRecoveryProvider)
    abstract = True
    name = ''
    id = ''
    
    def backup_now(self):
        Manager(self.app).backup_now(self)
        
    def backup(self, dir):
        pass
        
    def restore(self, dir):
        pass        
        

class Manager(Plugin):

    def __init__(self):
        try:
            self.dir = app.config.get('recovery', 'dir')
        except:
            self.dir = '/var/backups/ajenti'
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        
    def backup_now(self, provider):
        try:
            os.makedirs(os.path.join(self.dir, provider.id))
        except:
            pass
        dir = tempfile.mkdtemp()
        provider.backup(dir)
        if shell_status('cd %s; tar -cvpzf backup.tar.gz *'%dir) != 0:
            raise Exception()
            
        name = 0
        try:
            name = int(os.listdir(self.dir+'/'+provider.id)[0].split('.')[0])
        except:
            pass
            
        while os.path.exists('%s/%s/%i.tar.gz'%(self.dir,provider.id,name)):
            name += 1
            
        shutil.move('%s/backup.tar.gz'%dir, '%s/%s/%i.tar.gz'%(self.dir,provider.id,name))
        shutil.rmtree(dir)
        
    def restore_now(self, provider, revision):
        dir = tempfile.mkdtemp()
        shutil.copy('%s/%s/%i.tar.gz'%(self.dir,provider.id,revision), '%s/backup.tar.gz'%dir)
        if shell_status('cd %s; tar -xf backup.tar.gz'%dir) != 0:
            raise Exception()
        provider.restore(dir)
        shutil.rmtree(dir)
        
        
        
