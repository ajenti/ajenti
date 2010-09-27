import os
import tempfile
import shutil
import time

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
        

class BackupRevision:
    def __init__(self, rev, date):
        self.revision = rev
        self.date = time.strftime('%a, %d %b %Y %H:%M:%S', date)
        self._date = date

class Manager(Plugin):

    def __init__(self):
        try:
            self.dir = self.config.get('recovery', 'dir')
        except:
            self.dir = '/var/backups/ajenti'
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        
    def list_backups(self, id):
        r = []
        for x in os.listdir(os.path.join(self.dir, id)):
            r.append(BackupRevision(
                        x.split('.')[0], 
                        time.localtime(
                            os.path.getmtime(
                                os.path.join(self.dir, id, x)
                            )
                         )
                     ))
        return reversed(sorted(r, key=lambda x: x._date))

    def delete_backup(self, id, rev):
        try:
            os.unlink(os.path.join(self.dir, id, rev+'.tar.gz'))
        except:
            pass
        
    def find_provider(self, id):
        for x in self.app.grab_plugins(IRecoveryProvider):
            if x.id == id:
                return x
        
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
            
        shutil.move('%s/backup.tar.gz'%dir, '%s/%s/%s.tar.gz'%(self.dir,provider.id,name))
        shutil.rmtree(dir)
        
    def restore_now(self, provider, revision):
        dir = tempfile.mkdtemp()
        shutil.copy('%s/%s/%s.tar.gz'%(self.dir,provider.id,revision), '%s/backup.tar.gz'%dir)
        if shell_status('cd %s; tar -xf backup.tar.gz'%dir) != 0:
            raise Exception()
        provider.restore(dir)
        shutil.rmtree(dir)
        
        
        
