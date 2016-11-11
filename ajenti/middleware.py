import hashlib
import time
import random
import gevent
import pyotp

import ajenti
from ajenti.api import *
from ajenti.cookies import Cookie, Cookies
from ajenti.plugins import manager
from ajenti.http import HttpHandler
from ajenti.users import UserManager


class Session (object):
    """
    Holds the HTTP session data
    """

    def __init__(self, manager, id):
        self.touch()
        self.id = id
        self.data = {}
        self.active = True
        self.manager = manager
        self.greenlets = []

    def destroy(self):
        """
        Marks this session as dead
        """
        self.active = False
        for g in self.greenlets:
            g.kill()
        self.manager.vacuum()

    def touch(self):
        """
        Updates the "last used" timestamp
        """
        self.timestamp = time.time()

    def spawn(self, *args, **kwargs):
        """
        Spawns a ``greenlet`` that will be stopped and garbage-collected when the session is destroyed

        :params: Same as for :func:`gevent.spawn`
        """
        g = gevent.spawn(*args, **kwargs)
        self.greenlets += [g]

    def is_dead(self):
        return not self.active or (time.time() - self.timestamp) > 3600

    def set_cookie(self, context):
        """
        Adds headers to :class:`ajenti.http.HttpContext` that set the session cookie
        """
        context.add_header('Set-Cookie', Cookie('session', self.id, path='/', httponly=True).render_response())


@plugin
@persistent
@rootcontext
class SessionMiddleware (HttpHandler):
    def __init__(self):
        self.sessions = {}

    def generate_session_id(self, context):
        hash = str(random.random())
        hash += context.env.get('REMOTE_ADDR', '')
        hash += context.env.get('REMOTE_HOST', '')
        hash += context.env.get('HTTP_USER_AGENT', '')
        hash += context.env.get('HTTP_HOST', '')
        return hashlib.sha1(hash).hexdigest()

    def vacuum(self):
        """
        Eliminates dead sessions
        """
        for session in [x for x in self.sessions.values() if x.is_dead()]:
            del self.sessions[session.id]

    def open_session(self, context):
        """
        Creates a new session for the :class:`ajenti.http.HttpContext`
        """
        session_id = self.generate_session_id(context)
        session = Session(self, session_id)
        self.sessions[session_id] = session
        return session

    def handle(self, context):
        self.vacuum()
        cookie_str = context.env.get('HTTP_COOKIE', None)
        context.session = None
        if cookie_str:
            cookie = Cookies.from_request(
                cookie_str,
                ignore_bad_cookies=True,
            ).get('session', None)
            if cookie and cookie.value:
                if cookie.value in self.sessions:
                    # Session found
                    context.session = self.sessions[cookie.value]
                    if context.session.is_dead():
                        context.session = None
        if context.session is None:
            context.session = self.open_session(context)
        context.session.set_cookie(context)
        context.session.touch()


@plugin
@persistent
@rootcontext
class AuthenticationMiddleware (HttpHandler):
    def handle(self, context):
        if not hasattr(context.session, 'identity'):
            if ajenti.config.tree.authentication:
                context.session.identity = None
            else:
                context.session.identity = 'root'
                context.session.appcontext = AppContext(manager.context, context)

        if context.session.identity:
            context.add_header('X-Auth-Status', 'ok')
            context.add_header('X-Auth-Identity', str(context.session.identity))
        else:
            context.add_header('X-Auth-Status', 'none')

    def try_login(self, context, username, password, env=None):
        if UserManager.get().check_password(username, password, env=env):
            userdata = ajenti.config.tree.users[username]
            if(userdata.otp_config != None):
                return 'OTP_REQUIRED'
            self.login(context, username)
            return 'SUCCESS'
        return 'FAILED'

    def verify_otp_challange(self, context, username, token):
        if not username or not token:
            return False

        if not username in ajenti.config.tree.users:
            return False

        userdata = ajenti.config.tree.users[username]
        if userdata.otp_config == None:
            return False

        if userdata.otp_config['type'] == 'TOTP':
            totp = pyotp.TOTP(userdata.otp_config['secret'])
            if totp.verify(token):
                self.login(context, username)
                return True

        return False

    def login(self, context, username):
        context.session.identity = username
        context.session.appcontext = AppContext(manager.context, context)

    def logout(self, context):
        context.session.identity = None


__all__ = ['Session', 'SessionMiddleware', 'AuthenticationMiddleware']
