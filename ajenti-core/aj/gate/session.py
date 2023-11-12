import time
import logging
from http.cookies import SimpleCookie

from aj.gate.gate import WorkerGate


class Session():
    """
    Holds the HTTP session data
    """

    last_id = 0

    def __init__(self, key, gateway_middleware=None, client_info=None, auth_info=None, session_max_time=3600, **kwargs):
        Session.last_id += 1
        self.id = Session.last_id
        self.key = key
        self.client_info = client_info or {}
        self.data = {}
        self.identity = kwargs.get('initial_identity', None)
        self.auth_info = auth_info
        self.touch()
        self.active = True
        logging.info(
            f"Opening a new worker gate for session {self.id}, "
            f"client {self.client_info['address']}"
        )
        self.gate = WorkerGate(
            self,
            gateway_middleware=gateway_middleware,
            name=f'session {self.id:d}',
            log_tag='worker',
            **kwargs
        )
        self.session_max_time = session_max_time
        self.gate.start()
        logging.debug(f'New session {self.id}')

    def destroy(self):
        logging.debug(f'Destroying session {self.id}')
        self.gate.stop()

    def deactivate(self):
        """
        Marks this session as dead
        """
        self.active = False

    def touch(self):
        """
        Updates the "last used" timestamp
        """
        self.timestamp = time.time()

    def get_age(self):
        return time.time() - self.timestamp

    def is_dead(self):
        return not self.active or self.get_age() > self.session_max_time

    def set_cookie(self, http_context):
        """
        Adds headers to :class:`aj.http.HttpContext` that set
        the session cookie
        """

        cookie = SimpleCookie()
        cookie['session'] = self.key
        cookie['session']['path'] = '/'
        cookie['session']['httponly'] = True
        http_context.add_header('Set-Cookie', cookie.output(header=''))

    def serialize(self):
        return {
            'key':self.key,
            'identity':self.identity,
            'timestamp':self.timestamp,
            'client_info':self.client_info
        }
