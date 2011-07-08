import os
import glob
import tempfile
import shutil
import time

from ajenti.com import *
from ajenti.api import *
from ajenti.utils import shell, shell_status


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

    def find_provider(self, id):
        return ConfManager.get().get_configurable(id)
        
    def delete_backup(self, id, rev):
        os.unlink(os.path.join(self.dir, id, rev+'.tar.gz'))
        
    def backup_all(self):
        errs = []
        for x in self.app.grab_plugins(IConfigurable):
            try:
                self.backup(x)
            except:
                errs.append(x.name)
        return errs
        
    def backup(self, provider):
        try:
            os.makedirs(os.path.join(self.dir, provider.id))
        except:
            pass
        dir = tempfile.mkdtemp()
        
        try:
            for f in provider.list_files():
                for x in glob.glob(f):
                    shell('cp --parents -r \'%s\' \'%s\'' % (x, dir))

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
            raise
        finally:
            shutil.rmtree(dir)
        
    def restore(self, provider, revision):
        dir = tempfile.mkdtemp()
        shutil.copy('%s/%s/%s.tar.gz'%(self.dir,provider.id,revision), '%s/backup.tar.gz'%dir)
        for f in provider.list_files():
            for x in glob.glob(f):
                os.unlink(x)
        if shell_status('cd %s; tar -xf backup.tar.gz -C /'%dir) != 0:
            raise Exception()
        os.unlink('%s/backup.tar.gz'%dir)
        shutil.rmtree(dir)

class RecoveryHook (ConfMgrHook):
    def finished(self, cfg):
        Manager(self.app).backup(cfg)
        
