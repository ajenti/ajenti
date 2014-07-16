import grp
import logging
import os
import pwd
import re
import subprocess
import stat
import shutil
from datetime import datetime

from ajenti.api import *
from ajenti.util import str_fsize
from ajenti.plugins import manager
from ajenti.plugins.tasks.manager import TaskManager
from ajenti.plugins.tasks.tasks import CopyFilesTask, MoveFilesTask, DeleteFilesTask


class Item (object):
    stat_bits = [
        stat.S_IRUSR,
        stat.S_IWUSR,
        stat.S_IXUSR,
        stat.S_IRGRP,
        stat.S_IWGRP,
        stat.S_IXGRP,
        stat.S_IROTH,
        stat.S_IWOTH,
        stat.S_IXOTH,
    ]

    def __init__(self, path):
        self.checked = False
        self.path, self.name = os.path.split(path)
        self.fullpath = path
        self.isdir = os.path.isdir(path)
        self.icon = 'folder-close' if self.isdir else 'file'
        try:
            self.size = 0 if self.isdir else os.path.getsize(path)
        except OSError:
            self.size = 0
        self.sizestr = '' if self.isdir else str_fsize(self.size)
        self.mtime = datetime.utcfromtimestamp(os.stat(path).st_mtime)
        self.atime = datetime.utcfromtimestamp(os.stat(path).st_atime)
        self.ctime = datetime.utcfromtimestamp(os.stat(path).st_ctime)

    def read(self):
        stat = os.stat(self.fullpath)

        try:
            self.owner = pwd.getpwuid(stat.st_uid)[0]
        except KeyError:
            self.owner = str(stat.st_uid)

        try:
            self.group = grp.getgrgid(stat.st_gid)[0]
        except KeyError:
            self.group = str(stat.st_gid)

        self.mod_ur, self.mod_uw, self.mod_ux, \
            self.mod_gr, self.mod_gw, self.mod_gx, \
            self.mod_ar, self.mod_aw, self.mod_ax = [
                (stat.st_mode & Item.stat_bits[i] != 0)
                for i in range(0, 9)
            ]

    @property
    def mode(self):
        mods = [
            self.mod_ur, self.mod_uw, self.mod_ux,
            self.mod_gr, self.mod_gw, self.mod_gx,
            self.mod_ar, self.mod_aw, self.mod_ax
        ]
        return sum(
            Item.stat_bits[i] * (1 if mods[i] else 0)
            for i in range(0, 9)
        )

    def write(self):
        newpath = os.path.join(self.path, self.name)
        if self.fullpath != newpath:
            logging.info('[fm] renaming %s -> %s' % (self.fullpath, newpath))
            os.rename(self.fullpath, newpath)
        self.fullpath = os.path.join(self.path, self.name)
        os.chmod(self.fullpath, self.mode)

        err = None

        try:
            uid = int(self.owner or -1)
        except:
            try:
                uid = pwd.getpwnam(self.owner)[2]
            except KeyError:
                uid = -1
                err = Exception('Invalid owner')
        try:
            gid = int(self.group or -1)
        except:
            try:
                gid = grp.getgrnam(self.group)[2]
            except KeyError:
                gid = -1
                err = Exception('Invalid group')

        os.chown(self.fullpath, uid, gid)
        if err:
            raise err


@plugin
class FMBackend (BasePlugin):
    FG_OPERATION_LIMIT = 1024 * 1024 * 50

    def _escape(self, i):
        if hasattr(i, 'fullpath'):
            i = i.fullpath
        return '\'%s\' ' % i.replace("'", "\\'")

    def _total_size(self, items):
        return sum(_.size for _ in items)

    def _has_dirs(self, items):
        return any(_.isdir for _ in items)

    def init(self):
        self.task_manager = TaskManager.get()

    def remove(self, items, cb=lambda t: None):
        logging.info('[fm] removing %s' % ', '.join(x.fullpath for x in items))
        if self._total_size(items) > self.FG_OPERATION_LIMIT or self._has_dirs(items):
            paths = [x.fullpath for x in items]
            task = DeleteFilesTask.new(source=paths)
            task.callback = cb
            self.task_manager.run(task=task)
        else:
            for i in items:
                if os.path.isdir(i.fullpath):
                    shutil.rmtree(i.fullpath)
                else:
                    os.unlink(i.fullpath)
            cb(None)

    def move(self, items, dest, cb=lambda t: None):
        logging.info('[fm] moving %s to %s' % (', '.join(x.fullpath for x in items), dest))
        if self._total_size(items) > self.FG_OPERATION_LIMIT or self._has_dirs(items):
            paths = [x.fullpath for x in items]
            task = MoveFilesTask.new(source=paths, destination=dest)
            task.callback = cb
            self.task_manager.run(task=task)
        else:
            for i in items:
                shutil.move(i.fullpath, dest)
            cb(None)

    def copy(self, items, dest, cb=lambda t: None):
        logging.info('[fm] copying %s to %s' % (', '.join(x.fullpath for x in items), dest))
        if self._total_size(items) > self.FG_OPERATION_LIMIT or self._has_dirs(items):
            paths = [x.fullpath for x in items]
            task = CopyFilesTask.new(source=paths, destination=dest)
            task.callback = cb
            self.task_manager.run(task=task)
        else:
            for i in items:
                if os.path.isdir(i.fullpath):
                    shutil.copytree(i.fullpath, os.path.join(dest, i.name))
                else:
                    shutil.copy(i.fullpath, os.path.join(dest, i.name))
            cb(None)


@interface
class Unpacker (BasePlugin):
    @staticmethod
    def find(fn):
        for u in Unpacker.get_all():
            if u.match(fn):
                return u

    def match(self, fn):
        pass

    def unpack(self, path, cb=lambda: None):
        pass


@plugin
class TarUnpacker (Unpacker):
    def match(self, fn):
        return any(re.match(x, fn) for x in [r'.+\.tar.gz', r'.+\.tgz', r'.+\.tar'])

    def unpack(self, fn, cb=lambda: None):
        self.context.launch('terminal', command='cd "%s"; tar xvf "%s"' % os.path.split(fn), callback=cb)


@plugin
class ZipUnpacker (Unpacker):
    def match(self, fn):
        return any(re.match(x, fn) for x in [r'.+\.zip'])

    def unpack(self, fn, cb=lambda: None):
        self.context.launch('terminal', command='cd "%s"; unzip "%s"' % os.path.split(fn), callback=cb)