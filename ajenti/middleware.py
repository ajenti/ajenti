import hashlib
import time
import Cookie
import random

from ajenti.http import HttpHandler



class Session:
    def __init__(self):
        self.touch()

    def touch(self):
        self.timestamp = time.time()

    def is_dead(self):
        return (time.time() - self.timestamp) > 3600


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
        for session in [x for x in self.sessions if x.is_dead()]:
            self.sessions.remove(x)
            
    def handle(self, context):
        cookie = Cookie.SimpleCookie(context.env.get('HTTP_COOKIE')).get('session')
        if cookie is not None:
            session_id = cookie.value
        else:
            session_id = self.generate_session_id(context)
            self.sessions[session_id] = Session()
        context.session = self.sessions[session_id]


class AuthenticationMiddleware (HttpHandler):
    def handle(self, context):
        pass