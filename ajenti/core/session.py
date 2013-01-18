# encoding: utf-8
#
# Copyright (C) 2010 Dmitry Zamaruev (dmitry.zamaruev@gmail.com)


"""
This module provides simple session handling and WSGI Middleware.
You should instantiate SessionStore, and pass it to WSGI middleware
along with next WSGI application in chain.
Example:
>>> environ = {}
>>>
>>> def my_start_response(status, headers):
...     environ['HTTP_COOKIE'] = headers[0][1]
...
>>> def my_application(env, sr):
...     print("var = " + env['app.session'].get('var','None'))
...     env['app.session']['var'] = environ.get('REMOTE_ADDR', 'Test')
...     sr('200 OK',[])
...     return None  # Just for test, please return string
...
>>> s = SessionStore()
>>>
>>> SessionManager(s, my_application)(environ, my_start_response)
var = None
>>> SessionManager(s, my_application)(environ, my_start_response)
var = Test
>>>
>>> environ['REMOTE_ADDR'] = '127.0.0.1'
>>> SessionManager(s, my_application)(environ, my_start_response)
var = None
>>> SessionManager(s, my_application)(environ, my_start_response)
var = 127.0.0.1
>>> cookie = environ['HTTP_COOKIE']
>>>
>>> environ['REMOTE_ADDR'] = '127.0.0.2'
>>> SessionManager(s, my_application)(environ, my_start_response)
var = None
>>> environ['HTTP_COOKIE'] = None
>>> SessionManager(s, my_application)(environ, my_start_response)
var = None
>>>
>>> environ['REMOTE_ADDR'] = '127.0.0.1'
>>> environ['HTTP_COOKIE'] = cookie
>>> SessionManager(s, my_application)(environ, my_start_response)
var = 127.0.0.1
>>>
"""
import os
import time
import Cookie
import hashlib
from ajenti.utils import ClassProxy


def sha1(var):
    return hashlib.sha1(str(var)).hexdigest()


class SessionProxy(object):
    """ SessionProxy used to automatically add prefixes to keys

    >>> sess = Session('')
    >>> proxy = sess.proxy('test')
    >>> proxy['123'] = 'value'
    >>> sess
    {'test-123': 'value'}
    >>> proxy.get('123')
    'value'
    >>> proxy['123']
    'value'
    >>>
    """
    def __init__(self, session, prefix):
        self._session = session
        self._prefix = prefix + '-'

    def __getitem__(self, key):
        return self._session[self._prefix + key]

    def __setitem__(self, key, value):
        self._session[self._prefix + key] = value

    def get(self, key, default=None):
        return self._session.get(self._prefix + key, default)


class Session(dict):
    """ Session object
    Holds data between requests
    """
    def __init__(self, id):
        dict.__init__(self)
        self._id = id
        self._creationTime = self._accessTime = time.time()

    @property
    def id(self):
        """ Session ID """
        return self._id

    @property
    def creationTime(self):
        """ Session create time """
        return self._creationTime

    @property
    def accessTime(self):
        """ Session last access time """
        return self._accessTime

    def touch(self):
        self._accessTime = time.time()

    def proxy(self, prefix):
        return SessionProxy(self, prefix)

    @staticmethod
    def generateId():
        return sha1(os.urandom(40))


class SessionStore(object):
    """ Manages multiple session objects
    """
    # TODO: add session deletion/invalidation
    def __init__(self, timeout=30):
        # Default timeout is 30 minutes
        # Use internal timeout in seconds (for easier calculations)
        self._timeout = timeout*60
        self._store = {}

    @staticmethod
    def init_safe():
        """ Create a thread-safe SessionStore """
        return ClassProxy(SessionStore())

    def create(self):
        """ Create a new session,
        you should commit session to save it for future
        """
        sessId = Session.generateId()
        return Session(sessId)

    def checkout(self, id):
        """ Checkout session for use,
        you should commit session to save it for future
        """
        sess = self._store.get(id)

        if sess is not None:
            sess.touch()

        return sess

    def commit(self, session):
        """ Saves session for future use (useful in database backends)
        """
        self._store[session.id] = session

    def vacuum(self):
        """ Goes through all sessions and deletes all old sessions
        Should be called periodically
        """
        ctime = time.time()
        # We should use .keys() here, because we could change size of dict
        for sessId in self._store.keys():
            if (ctime - self._store[sessId].accessTime) > self._timeout:
                del self._store[sessId]


class SessionManager(object):
    """
    Session middleware. Takes care of creation/checkout/commit of a session.
    Sets 'app.session' variable inside WSGI environment.
    """
    # TODO: Add cookie expiration and force expiration
    # TODO: Add deletion of invalid session
    def __init__(self, store, application):
        """ Initializes SessionManager

        @store - instance of SessionStore
        @application - wsgi dispatcher callable
        """
        self._session_store = store
        self._application = application
        self._session = None
        self._start_response_args = ('200 OK', [])

    def add_cookie(self, headers):
        if self._session is None:
            raise RuntimeError('Attempt to save non-initialized session!')

        sess_id = self._session.id
        C = Cookie.SimpleCookie()
        C['sess'] = sess_id
        C['sess']['path'] = '/'

        headers.append(('Set-Cookie',C['sess'].OutputString()))

    def start_response(self, status, headers):
        self.add_cookie(headers)
        self._start_response_args = (status, headers)

    def _load_session_cookie(self, environ):
        cookie_str = environ.get('HTTP_COOKIE')
        cookie_str = cookie_str.replace('&', '_')
        C = Cookie.SimpleCookie(cookie_str)
        cookie = C.get('sess')
        if cookie is not None:
            self._session = self._session_store.checkout(cookie.value)

    def _get_client_id(self, environ):
        hash = 'salt'
        hash += environ.get('REMOTE_ADDR', '')
        hash += environ.get('REMOTE_HOST', '')
        hash += environ.get('HTTP_USER_AGENT', '')
        hash += environ.get('HTTP_HOST', '')
        return sha1(hash)

    def _get_session(self, environ):
        # Load session from cookie
        self._load_session_cookie(environ)

        # Check is session exists and valid
        client_id = self._get_client_id(environ)
        if self._session is not None:
            if self._session.get('client_id','') != client_id:
                self._session = None

        # Create session
        if self._session is None:
            self._session = self._session_store.create()
            self._session['client_id'] = client_id

        return self._session

    def __call__(self, environ, start_response):
        self.start_response_origin = start_response
        self._session_store.vacuum()
        sess = self._get_session(environ)
        environ['app.session'] = sess

        result = None
        try:
            result = self._application(environ, self.start_response)
        finally:
            self._session_store.commit(self._session)

        self.start_response_origin(*self._start_response_args)
        return result
