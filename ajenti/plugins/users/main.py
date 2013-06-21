import subprocess

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import PasswdConfig, GroupConfig


@plugin
class Users (SectionPlugin):
    def init(self):
        self.title = _('Users')
        self.icon = 'group'
        self.category = _('System')
        self.append(self.ui.inflate('users:main'))

        def _sorter(x):
            u = int(x.uid)
            if u >= 1000:
                return u - 10000
            return u

        self.find('users').sorting = _sorter

        self.config = PasswdConfig(path='/etc/passwd')
        self.config_g = GroupConfig(path='/etc/group')
        self.binder = Binder(None, self.find('passwd-config'))
        self.binder_g = Binder(None, self.find('group-config'))

        self.mgr = UsersBackend.get()

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self.config_g.load()

        self.binder.reset(self.config.tree).autodiscover().populate()
        self.binder_g.reset(self.config_g.tree).autodiscover().populate()

    @on('add-user', 'click')
    def on_add_user(self):
        self.find('input-username').visible = True

    @on('input-username', 'submit')
    def on_add_user_done(self, value):
        self.mgr.add_user(value)
        self.refresh()

    @on('add-group', 'click')
    def on_add_group(self):
        self.find('input-groupname').visible = True

    @on('input-groupname', 'submit')
    def on_add_group_done(self, value):
        self.mgr.add_group(value)
        self.refresh()

    @on('save-users', 'click')
    def save_users(self):
        self.binder.update()
        self.config.save()

    @on('save-groups', 'click')
    def save_groups(self):
        self.binder_g.update()
        self.config_g.save()


@interface
class UsersBackend (object):
    def add_user(self, name):
        pass

    def add_group(self, name):
        pass


@plugin
class LinuxUsersBackend (UsersBackend):
    platforms = ['debian', 'centos']

    def add_user(self, name):
        subprocess.call(['useradd', name])

    def add_group(self, name):
        subprocess.call(['groupadd', name])


@plugin
class BSDUsersBackend (UsersBackend):
    platforms = ['freebsd']

    def add_user(self, name):
        subprocess.call(['pw', 'useradd', name])

    def add_group(self, name):
        subprocess.call(['pw', 'groupadd', name])
