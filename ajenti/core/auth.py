from hashlib import sha1
from base64 import b64decode, b64encode
from binascii import hexlify
from random import random
import syslog
import time

from ajenti.api import get_environment_vars


def check_password(passw, hash):
    if hash.startswith('{SHA}'):
        try:
            hash = hash[5:]
            hash = b64decode(hash)
            passw_hash = sha1(passw).digest()
            if passw_hash == hash:
                return True
        except:
            import traceback
            traceback.print_exc()
    return False


class AuthManager(object):
    """
    Authentication middleware which takes care of user authentication

    Instance vars:

    - ``user`` - `str`, current user logged in or None
    """

    def __init__(self, config, app, dispatcher):
        self.user = None

        self.app = app
        app.auth = self
        self._dispatcher = dispatcher
        self._log = config.get('log_facility')

        self._config = config
        self._enabled = False
        if config.has_option('ajenti', 'auth_enabled'):
            if config.getint('ajenti', 'auth_enabled'):
                # Check for 'users' section
                if config.has_section('users'):
                    if len(config.items('users')) > 0:
                        self._enabled = True
                    else:
                        self._log.error('Authentication requested, but no users configured')
                else:
                    self._log.error('Authentication requested, but no [users] section')

    def deauth(self):
        """
        Deauthenticates current user.
        """
        self.app.session['auth.user'] = None

    def __call__(self, environ, start_response):
        session = environ['app.session']
        if 'auth.challenge' in session:
            challenge = session['auth.challenge']
        else:
            challenge = b64encode(sha1(str(random())).digest())
            session['auth.challenge'] = challenge

        if environ['PATH_INFO'] == '/auth-redirect':
            start_response('301 Moved Permanently', [('Location', '/')])
            return ''

        self.user = session['auth.user'] if 'auth.user' in session else None
        if not self._enabled:
            self.user = 'anonymous'
        if self.user is not None or environ['PATH_INFO'].startswith('/dl') \
            or environ['PATH_INFO'].startswith('/core'):
            return self._dispatcher(environ, start_response)

        if environ['PATH_INFO'] == '/auth':
            vars = get_environment_vars(environ)
            user = vars.getvalue('username', '')
            if self._config.has_option('users', user):
                pwd = self._config.get('users', user)[5:]
                pwd = hexlify(b64decode(pwd))
                sample = hexlify(sha1(challenge + pwd).digest())
                resp = vars.getvalue('response', '')
                if sample == resp:
                    syslog.syslog('session opened for user %s from %s' % (user, environ['REMOTE_ADDR']))
                    session['auth.user'] = user
                    start_response('200 OK', [
                        ('Content-type','text/plain'),
                        ('X-Ajenti-Auth', 'ok'),
                    ])
                    return ''

            syslog.syslog('login failed for user %s from %s' % (user, environ['REMOTE_ADDR']))
            time.sleep(4)

            start_response('200 OK', [
                ('Content-type','text/plain'),
                ('X-Ajenti-Auth', 'fail'),
            ])
            return 'Login failed'

        templ = self.app.get_template('auth.xml')
        templ.find('challenge').set('value', challenge)
        start_response('200 OK', [('Content-type','text/html')])
        start_response('200 OK', [
            ('Content-type','text/html'),
            ('X-Ajenti-Auth', 'start'),
            ('X-Ajenti-Challenge', challenge),
        ])
        return templ.render()
