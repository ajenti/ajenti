import os
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

        def _filterOnlyUsers(x):
            u = int(x.uid)
            return u >= 500

        def _filterOnlySystemUsers(x):
            u = int(x.uid)
            return u < 500

        def _sorter(x):
            g = int(x.gid)
            if g >= 500:
                return g - 10000
            return g

        self.find('users').filter = _filterOnlyUsers
        self.find('system-users').filter = _filterOnlySystemUsers
        self.find('groups').sorting = _sorter

        self.config = PasswdConfig(path='/etc/passwd')
        self.config_g = GroupConfig(path='/etc/group')
        self.binder = Binder(None, self.find('passwd-config'))
        self.binder_system = Binder(None, self.find('passwd-config-system'))
        self.binder_g = Binder(None, self.find('group-config'))

        self.mgr = UsersBackend.get()

        def post_item_bind(object, collection, item, ui):
            ui.find('change-password').on('click', self.change_password, item, ui)
            ui.find('remove-password').on('click', self.remove_password, item)
            if not os.path.exists(item.home):
                ui.find('create-home-dir').on('click', self.create_home_dir, item, ui)
                ui.find('create-home-dir').visible = True

        self.find('users').post_item_bind = post_item_bind
        self.find('system-users').post_item_bind = post_item_bind

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self.config_g.load()

        self.binder.reset(self.config.tree).autodiscover().populate()
        self.binder_system.reset(self.config.tree).autodiscover().populate()
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
    @on('save-system-users', 'click')
    def save_users(self):
        self.binder.update()
        self.binder_system.update()
        self.config.save()

    @on('save-groups', 'click')
    def save_groups(self):
        self.binder_g.update()
        self.config_g.save()

    def create_home_dir(self, user, ui):
        self.mgr.make_home_dir(user)
        self.context.notify('info', _('Home dir for %s was created') % user.name)
        ui.find('create-home-dir').visible = False

    def change_password(self, user, ui):
        new_password = ui.find('new-password').value

        if new_password:
            try:
                self.mgr.change_password(user, new_password)
                self.context.notify('info', _('Password for %s was changed') % user.name)
                ui.find('new-password').value = ''
            except Exception, e:
                self.context.notify('error', _('Error: "%s"') % e.message)
        else:
            self.context.notify('error', _('Password shouldn\'t be empty'))

    def remove_password(self, user):
        self.mgr.remove_password(user)
        self.context.notify('info', _('Password for %s was removed') % user.name)


@interface
class UsersBackend (object):
    def add_user(self, name):
        pass

    def add_group(self, name):
        pass

    def set_home(self, user):
        pass

    def change_password(self, user, password):
        proc = subprocess.Popen(
            ['passwd', user.name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate('%s\n%s\n' % (password, password))
        if proc.returncode:
            raise Exception(stderr)

    def remove_password(self, user):
        subprocess.call(['passwd', '-d', user.name])

    def make_home_dir(self, user):
        subprocess.call(['mkdir', '-p', user.home])
        subprocess.call(['chown', '%s:%s' % (user.uid, user.gid), user.home])
        self.set_home(user)


@plugin
class LinuxUsersBackend (UsersBackend):
    platforms = ['debian', 'centos', 'arch']

    def add_user(self, name):
        subprocess.call(['useradd', '-s', '/bin/false', name])

    def add_group(self, name):
        subprocess.call(['groupadd', name])

    def set_home(self, user):
        subprocess.call(['usermod', '-d', user.home, '-m', user.name])


@plugin
class BSDUsersBackend (UsersBackend):
    platforms = ['freebsd']

    def add_user(self, name):
        subprocess.call(['pw', 'useradd', '-s', '/bin/false', name])

    def add_group(self, name):
        subprocess.call(['pw', 'groupadd', name])

    def set_home(self, user):
        subprocess.call(['pw', 'usermod', '-d', user.home, '-m', user.name])
