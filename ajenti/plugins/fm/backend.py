import shutil
import os
import subprocess
import stat
import pwd
import grp

from ajenti.api import *
from ajenti.util import str_fsize


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
        os.rename(self.fullpath, os.path.join(self.path, self.name))
        self.fullpath = os.path.join(self.path, self.name)
        os.chmod(self.fullpath, self.mode)
        
        try:
            uid = int(self.owner)
        except:
            uid = pwd.getpwnam(self.owner)[2]
        try:
            gid = int(self.group)
        except:
            gid = grp.getgrnam(self.group)[2]

        os.chown(self.fullpath, uid, gid)


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

    def remove(self, items, cb=lambda: None):
        if self._total_size(items) > self.FG_OPERATION_LIMIT or self._has_dirs(items):
            command = 'rm -vfr -- '
            for item in items:
                command += self._escape(item)
            self.context.launch('terminal', command=command, callback=cb)
        else:
            for i in items:
                if os.path.isdir(i.fullpath):
                    shutil.rmtree(i.fullpath)
                else:
                    os.unlink(i.fullpath)
            cb()

    def move(self, items, dest, cb=lambda: None):
        if self._total_size(items) > self.FG_OPERATION_LIMIT or self._has_dirs(items):
            command = 'mv -v -- '
            for item in items:
                command += self._escape(item)
            command += self._escape(dest)
            self.context.launch('terminal', command=command)
        else:
            for i in items:
                shutil.move(i.fullpath, dest, callback=cb)
            cb()

    def copy(self, items, dest, cb=lambda: None):
        if self._total_size(items) > self.FG_OPERATION_LIMIT or self._has_dirs(items):
            command = 'cp -rv -- '
            for item in items:
                command += self._escape(item)
            command += self._escape(dest)
            if subprocess.call(['which', 'vcp']) == 0:
                command = 'v' + command
            self.context.launch('terminal', command=command, callback=cb)
        else:
            for i in items:
                if os.path.isdir(i.fullpath):
                    shutil.copytree(i.fullpath, os.path.join(dest, i.name))
                else:
                    shutil.copy(i.fullpath, os.path.join(dest, i.name))
            cb()
