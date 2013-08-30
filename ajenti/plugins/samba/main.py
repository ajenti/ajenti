from ajenti.api import *
from ajenti.ui.binder import Binder
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.util import platform_select

from reconfigure.configs import SambaConfig, PasswdConfig
from reconfigure.items.samba import ShareData

from status import SambaMonitor
from smbusers import SambaUsers


@plugin
class Samba (SectionPlugin):
    def init(self):
        self.title = 'Samba'
        self.icon = 'folder-close'
        self.category = _('Software')
        self.append(self.ui.inflate('samba:main'))

        self.find('servicebar').name = platform_select(
            debian='samba',
            ubuntu='smbd',
            centos='smb',
            default='samba',
        )
        self.find('servicebar').reload()

        self.binder = Binder(None, self.find('config'))
        self.find('shares').new_item = lambda c: ShareData()
        self.config = SambaConfig(path='/etc/samba/smb.conf')

        def post_item_bind(object, collection, item, ui):
            ui.find('disconnect').on('click', self.on_disconnect, item)

        self.find('connections').post_item_bind = post_item_bind

        def post_user_bind(object, collection, item, ui):
            def delete_user():
                self.usermgr.delete(item.username)
                self.refresh()
            ui.find('delete').on('click', delete_user)

            def set_password():
                if self.usermgr.set_password(item.username, ui.find('password').value):
                    self.context.notify('info', _('Password updated'))
                    ui.find('password').value = ''
                else:
                    self.context.notify('error', _('Password update failed'))
            ui.find('password-set').on('click', set_password)

        self.find('user-list').post_item_bind = post_user_bind

        self.usermgr = SambaUsers()
        self.binder_u = Binder(self.usermgr, self.find('users'))

        self.monitor = SambaMonitor()
        self.binder_m = Binder(self.monitor, self.find('status'))

    def on_page_load(self):
        self.refresh()

    def on_disconnect(self, connection):
        connection.disconnect()
        self.refresh()

    def refresh(self):
        self.config.load()
        self.monitor.refresh()
        self.usermgr.load()
        self.binder.reset(self.config.tree).autodiscover().populate()
        self.binder_m.reset(self.monitor).autodiscover().populate()
        self.binder_u.reset(self.usermgr).autodiscover().populate()

        users_dropdown = self.find('add-user-list')
        users = [x.name for x in PasswdConfig(path='/etc/passwd').load().tree.users]
        for u in self.usermgr.users:
            if u.username in users:
                users.remove(u.username)
        users_dropdown.values = users_dropdown.labels = users

    @on('add-user', 'click')
    def on_add_user(self):
        self.usermgr.create(self.find('add-user-list').value)
        self.refresh()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        self.config.save()
        self.refresh()
