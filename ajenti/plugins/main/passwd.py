import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.users import UserManager

import pyotp
import pyqrcode
import base64
import io
import platform

@plugin
class PasswordChangeSection (SectionPlugin):
    def init(self):
        self.title = _('Password')
        self.icon = 'lock'
        self.category = ''
        self.order = 51
        self.append(self.ui.inflate('main:passwd-main'))
        self.refreshOTPView()



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

    @on('reconfigure-otp', 'click')
    def reconfigureOTP(self):
        self.enableOTP()

    @on('enable-otp', 'click')
    def enableOTP(self):
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        dialog = self.find('dialog')

        username = self.context.session.identity

        buffer = io.BytesIO()
        uri = totp.provisioning_uri(username + "@" + platform.node())
        self.find('secret').value = uri
        qrcode = pyqrcode.create(uri)
        qrcode.svg(buffer)

        image = self.find('qrcode')
        image.src = "data:image/svg+xml;base64," + base64.b64encode(buffer.getvalue())

        self.find('dialog').visible = True

        def confirm(button=None):
            data = {
                'type': "TOTP",
                'secret': secret
            }

            ajenti.config.tree.users[username].otp_config = data
            ajenti.config.save()
            dialog.visible = False
            self.refreshOTPView()
            self.context.notify(
                'info',
                _('Two Factor Authentication enabled.')
            )

        dialog.on('button', confirm)

    @on('disable-otp', 'click')
    def disableOTP(self):
        username = self.context.session.identity
        ajenti.config.tree.users[username].otp_config = None
        ajenti.config.save()
        self.refreshOTPView()

    def refreshOTPView(self):
        username = self.context.session.identity
        has_otp = ajenti.config.tree.users[username].otp_config != None
        self.find('enable-otp').visible = not has_otp
        self.find('reconfigure-otp').visible = has_otp
        self.find('disable-otp').visible = has_otp