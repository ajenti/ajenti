from hashlib import sha1
from base64 import b64decode, b64encode
from binascii import hexlify
from random import random
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
    """ Authentication middleware
    Takes care of user authentication
    """
    def __init__(self, config, app, dispatcher):
        """ Initialize AuthManager

        @config - config instance (for auth/users/password)
        @application - wsgi dispatcher callable
        """
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
        if self.user is not None or environ['PATH_INFO'].startswith('/dl'):
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
                    session['auth.user'] = user
                    start_response('200 OK', [])
                    return ''

            start_response('200 OK', [])
            return 'Login failed'

        templ = self.app.get_template('auth.xml')
        templ.find('challenge').set('value', challenge)
        start_response('200 OK', [('Content-type','text/html')])
        return templ.render()
