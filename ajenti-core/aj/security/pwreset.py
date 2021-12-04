import logging
import os
from itsdangerous.url_safe import URLSafeTimedSerializer
from itsdangerous.exc import SignatureExpired, BadTimeSignature, BadSignature

import aj
from aj.auth import AuthenticationService
from aj.api.mail import Mail


SECRET_FILE = '/etc/ajenti/.secret'


class PasswordResetMiddleware():

    def __init__(self):
        self.context = aj.context
        self.auth_provider = AuthenticationService.get(self.context).get_provider()
        self.notifications = Mail()
        self.ensure_secret_key()

    def ensure_secret_key(self):
        """
        Generate secret key and provide basic length test.
        """

        if not os.path.isfile(SECRET_FILE):
            logging.info('No secret found, generating new secret key')
            with open(SECRET_FILE, 'w') as f:
                f.write(os.urandom(16).hex())
        else:
            with open(SECRET_FILE, 'r') as f:
                secret = f.read().strip('\n')
            if len(secret) < 32:
                logging.warning('Secret key is too weak, you need at least 32 chars')
        os.chmod(SECRET_FILE, 0o600)

    def send_password_reset(self, mail, origin):
        """
        Sends upstream a request to check if a given email exists, in order to
        send a password reset link per email.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        username = self.auth_provider.check_mail(mail)
        if username:
            with open(SECRET_FILE, 'r') as f:
                secret = f.read().strip('\n')
                serializer = URLSafeTimedSerializer(secret)
            serial = serializer.dumps({'user': username, 'email': mail})
            link = f'{origin}/view/reset_password/{serial}'
            self.notifications.send_password_reset(mail, link)

    def check_serial(self, serial):
        """
        Check if the serial in a given reset link is valid

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        if serial:
            try:
                with open(SECRET_FILE, 'r') as f:
                    secret = f.read().strip('\n')
                    serializer = URLSafeTimedSerializer(secret)
                    # Serial can not be used after 15 min
                data = serializer.loads(serial, max_age=900)
                return data
            except (SignatureExpired, BadTimeSignature, BadSignature) as err:
                 logging.warning('Password reset link not valid or expired')
                 return False
        return False


    def update_password(self, serial, password):
        """
        Update user's password in the auth provider.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        with open(SECRET_FILE, 'r') as f:
            secret = f.read().strip('\n')
            serializer = URLSafeTimedSerializer(secret)
        user = serializer.loads(serial, max_age=99900)['user']
        auth_provider = AuthenticationService.get(self.context).get_provider()
        return auth_provider.update_password(user, password)