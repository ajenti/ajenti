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


class SimpleFileRecoveryProvider(RecoveryProvider):
    abstract = True
    path = ''
    
    def backup(self, dir):
        shutil.copy(self.path, dir+'/data')
    
    def restore(self, dir):
        shutil.copy(dir+'/data', self.path)


class SimpleDirectoryRecoveryProvider(RecoveryProvider):
    abstract = True
    path = ''
    
    def backup(self, dir):
        shell('cp -r %s/* %s/'%(self.path,dir))
    
    def restore(self, dir):
        shell('rm %s/* -r'%self.path)
        shell('cp -r %s/* %s/'%(dir,self.path))
    

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
        if not os.path.exists(os.path.join(self.dir, id)):
            return r
            
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
        os.unlink(os.path.join(self.dir, id, rev+'.tar.gz'))
        
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
        
        try:
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
        except:
            raise Exception()
        finally:
            shutil.rmtree(dir)
        
    def restore_now(self, provider, revision):
        dir = tempfile.mkdtemp()
        shutil.copy('%s/%s/%s.tar.gz'%(self.dir,provider.id,revision), '%s/backup.tar.gz'%dir)
        if shell_status('cd %s; tar -xf backup.tar.gz'%dir) != 0:
            raise Exception()
        os.unlink('%s/backup.tar.gz'%dir)

        try:
            provider.restore(dir)
        except:
            raise
        finally:
            shutil.rmtree(dir)

