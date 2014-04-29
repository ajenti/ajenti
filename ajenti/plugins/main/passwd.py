import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.users import UserManager


@plugin
class PasswordChangeSection (SectionPlugin):
    def init(self):
        self.title = _('Password')
        self.icon = 'lock'
        self.category = ''
        self.order = 51
        self.append(self.ui.inflate('main:passwd-main'))

    @on('save', 'click')
    def save(self):
        new_password = self.find('new-password').value
        if new_password != self.find('new-password-2').value:
            self.context.notify('error', _('Passwords don\'t match'))
            return
        old_password = self.find('old-password').value
        if not UserManager.get().check_password(self.context.session.identity, old_password) or not new_password or not old_password:
            self.context.notify('error', _('Incorrect password'))
            return
        UserManager.get().set_password(self.context.session.identity, new_password)
        ajenti.config.save()
        self.context.notify('info', _('Password changed'))
