import logging
import os
import subprocess
import time

from ajenti.api import *

from api import Task, TaskError



@plugin
class CommandTask (Task):
    name = 'Execute command'
    ui = 'tasks:params-execute'
    default_params = {
        'command': '',
    }

    def run(self, command=None):
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        o,e = p.communicate()
        if p.returncode:
            raise TaskError(o + e)
        else:
            self.result.output = o


@plugin
class CopyFilesTask (Task):
    name = 'Copy files'
    ui = 'tasks:params-copydir'
    command = ['cp', '-rp']
    message_template = _('Copying %s')
    default_params = {
        'source': '',
        'destination': '',
    }

    def run(self, source=None, destination=None):
        index = 0
        files = os.listdir(source)
        if not os.path.exists(destination):
            os.makedirs(destination)
        if not destination.endswith('/'):
            destination += '/'

        for file in files:
            self.message = self.message_template % file
            srcpath = os.path.join(source, file)
            p = subprocess.Popen(self.command + [srcpath, destination])
            while p.poll() is None:
                time.sleep(1)
                if self.aborted:
                    p.terminate()
                    return
            index += 1
            self.set_progress(index, len(files))


@plugin
class MoveFilesTask (CopyFilesTask):
    name = 'Move files'
    command = ['mv']
    message_template = _('Moving %s')



@plugin
class RSyncTask (Task):
    name = 'RSync'
    ui = 'tasks:params-rsync'
    default_params = {
        'source': '',
        'destination': '',
        'archive': True,
        'recursive': True,
        'times': True,
        'xattrs': True,
        'delete': False,
        'perms': True,
    }

    def run(self, source=None, destination=None, **kwargs):
        cmd = ['rsync']
        for opt in ['archive', 'recursive', 'times', 'xattrs', 'delete', 'perms']:
            if kwargs.get(opt, self.default_params[opt]):
                cmd += ['--' + opt]
        cmd += [source, destination]
        logging.info('RSync: ' + ' '.join(cmd))
        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)  
        o, e = p.communicate()
        if p.returncode:
            raise TaskError(o + e)
