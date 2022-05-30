import logging
import pexpect
import pwd
import subprocess
import syslog
from functools import wraps
from jadi import component, service, interface

import aj
from aj.api.http import BaseHttpHandler
from aj.security.verifier import ClientCertificateVerificator
from aj.util import public

@public
class SudoError(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return self.message


@public
class SecurityError(Exception):
    def __init__(self, permission):
        Exception.__init__(self)
        self.message = f'Permission "{permission}" is required'

    def __str__(self):
        return self.message


@public
@service
class AuthenticationMiddleware(BaseHttpHandler):
    def __init__(self, context):
        self.context = context
        self.auth = AuthenticationService.get(self.context)
        if not hasattr(context, 'identity'):
            context.identity = None

    def handle(self, http_context):
        if http_context.env['SSL_CLIENT_VALID']:
            if not self.context.identity:
                username = http_context.env['SSL_CLIENT_USER']
                logging.info(
                    f'SSL client certificate {http_context.env["SSL_CLIENT_DIGEST"]}'
                    f' verified as {username}'
                )
                try:
                    pwd.getpwnam(username)
                    found = True
                except KeyError:
                    found = False
                if found:
                    self.auth.prepare_session_redirect(http_context, username, True)
                    #self.auth.login(username)

        http_context.add_header('X-Auth-Identity', str(self.context.identity or ''))


class AuthenticationError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


@interface
class AuthenticationProvider():
    id = None
    name = None
    allows_sudo_elevation = False

    def __init__(self, context):
        self.context = context

    def authenticate(self, username, password):
        raise NotImplementedError

    def authorize(self, username, permission):
        raise NotImplementedError

    def get_isolation_uid(self, username):
        raise NotImplementedError

    def get_isolation_gid(self, username):
        raise NotImplementedError

    def get_profile(self, username):
        raise NotImplementedError

    def check_mail(self, mail):
        raise NotImplementedError

    def check_password_complexity(self,password):
        raise NotImplementedError

    def update_password(self):
        raise NotImplementedError

    def prepare_environment(self, username):
        raise NotImplementedError

    def signout(self):
        raise NotImplementedError

@component(AuthenticationProvider)
class OSAuthenticationProvider(AuthenticationProvider):
    id = 'os'
    name = 'OS users'
    allows_sudo_elevation = True
    pw_reset = False

    def authenticate(self, username, password):
        child = None

        from shlex import quote

        try:
            child = pexpect.spawn(
                '/bin/sh',
                ['-c', f'/bin/su -c "/bin/echo SUCCESS" - {quote(username)}'],
                timeout=25
            )
            child.expect([
                b'.*:', # normal colon
                b'.*\xef\xb9\x95', # small colon
                b'.*\xef\xbc\x9a',  # fullwidth colon
            ])
            child.sendline(password)
            result = child.expect(['su: .*', 'SUCCESS'])
        except pexpect.exceptions.EOF as err:
            logging.error(f'Login error: {child.before.decode().strip()}')
            if child and child.isalive():
                child.close()
            return False
        except Exception as err:
            if child and child.isalive():
                child.close()
            logging.error(f'Error checking password: {err}')
            return False
        if result == 0:
            return False
        return True

    def authorize(self, username, permission):
        return True

    def prepare_environment(self, username):
        pass

    def get_isolation_uid(self, username):
        return pwd.getpwnam(username).pw_uid

    def get_isolation_gid(self, username):
        return None

    def check_password_complexity(self,password):
        # TODO : add password policy
        return True

    def get_profile(self, username):
        return {}

    def check_mail(self, mail):
        return False

    def update_password(self):
        pass

    def signout(self):
        pass


@public
@service
class AuthenticationService():
    def __init__(self, context):
        self.context = context

    def get_provider(self):
        provider_id = aj.config.data['auth'].get('provider', 'os')
        for provider in AuthenticationProvider.all(self.context):
            if provider.id == provider_id:
                return provider
        raise AuthenticationError(f'Authentication provider {provider_id} is unavailable')

    def check_password(self, username, password):
        return self.get_provider().authenticate(username, password)

    def check_sudo_password(self, username, password):
        if not aj.config.data['auth'].get('allow_sudo', False):
            return False
        sudo = subprocess.Popen(
            ['sudo', '-S', '-k', '-u', username, '--', 'ls'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        o, e = sudo.communicate(password.encode('utf-8') + b'\n')
        if sudo.returncode != 0:
            raise SudoError((o + e).decode('utf-8').splitlines()[-1].strip())
        return True

    def client_certificate_callback(self, connection, x509, errno, depth, result):
        if depth == 0 and (errno == 9 or errno == 10):
            return False  # expired / not yet valid
        if not aj.config.data['ssl']['client_auth']['force']:
            return True
        user = ClientCertificateVerificator.get(aj.context).verify(x509)
        return bool(user)

    def get_identity(self):
        return self.context.identity

    def login(self, username, demote=True):
        logging.info(f'Authenticating session as {username}')
        syslog.syslog(
            syslog.LOG_NOTICE | syslog.LOG_AUTH,
            f'{username} has logged in from {self.context.session.client_info["address"]}'
        )

        # Allow worker to perform operations as root before demoting
        self.get_provider().prepare_environment(username)

        if demote:
            uid = self.get_provider().get_isolation_uid(username)
            gid = self.get_provider().get_isolation_gid(username)
            logging.debug(
                f'Authentication provider "{self.get_provider().name}" maps "{username}" -> {uid:d}'
            )
            self.context.worker.demote(uid, gid)
        self.context.identity = username

    def prepare_session_redirect(self, http_context, username, auth_info):
        http_context.add_header('X-Session-Redirect', username)
        http_context.add_header('X-Auth-Info', auth_info)

@public
@interface
class PermissionProvider():
    def __init__(self, context):
        self.context = context

    def provide(self):
        return []


@public
class authorize():
    def __init__(self, permission_id):
        self.permission_id = permission_id

    def check(self):
        username = aj.worker.context.identity
        provider = AuthenticationService.get(aj.worker.context).get_provider()
        for permission in [
            p
            for permission_provider in PermissionProvider.all(aj.worker.context)
            for p in permission_provider.provide()
        ]:
            if permission['id'] == self.permission_id:
                if provider.authorize(username, permission):
                    break
                raise SecurityError(self.permission_id)
        else:
            raise SecurityError(self.permission_id)

    def __call__(self, fx):
        fx.permission_id = self.permission_id
        @wraps(fx)
        def wrapper(*args, **kwargs):
            self.check()
            return fx(*args, **kwargs)
        return wrapper

    def __enter__(self):
        self.check()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
