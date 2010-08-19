from hashlib import sha1
from base64 import b64decode

unauthorized_page="""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
 "http://www.w3.org/TR/1999/REC-html401-19991224/loose.dtd">
<HTML>
  <HEAD>
    <TITLE>Error</TITLE>
    <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=ISO-8859-1">
  </HEAD>
  <BODY><H1>401 Unauthorized.</H1></BODY>
</HTML>
"""

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
    def __init__(self, config, application):
        """ Initialize AuthManager

        @config - config instance (for auth/users/password)
        @application - wsgi dispatcher callable
        """
        self._application = application
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
        if self._enabled:
            self._log.info("Enabling authentication")
        else:
            self._log.info("Disabling authentication")

    def __call__(self, environ, start_response):
        if self._enabled:
            authorized = False
            # Check auth
            if 'HTTP_AUTHORIZATION' in environ:
                (scheme, hash) = environ.get('HTTP_AUTHORIZATION').split()
                if scheme == 'Basic':
                    (user, passw) = b64decode(hash).split(':',1)
                    if self._config.has_option('users', user):
                        hash_passw = self._config.get('users', user)
                        if check_password(passw, hash_passw):
                            authorized = True
                else:
                    self._log.debug('Wrong auth scheme "%s"'%scheme)
            # Request auth
            if not authorized:
                start_response('401 Authorization Required',
                               [('WWW-Authenticate','Basic realm="Ajenti"'),
                                ('Content-type','text/html')])
                return [unauthorized_page]
            environ['HTTP_USER'] = user

        # Dispatch request
        return self._application(environ, start_response)

