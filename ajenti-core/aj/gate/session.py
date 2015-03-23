import time
import logging
from cookies import Cookie

from aj.gate.gate import WorkerGate


class Session(object):
    """
    Holds the HTTP session data
    """

    last_id = 0

    def __init__(self, key, client_info=None, **kwargs):
        Session.last_id += 1
        self.id = Session.last_id
        self.key = key
        self.client_info = client_info or {}
        self.data = {}
        self.identity = None
        self.touch()
        self.active = True
        logging.info(
            'Opening a new worker gate for session %s, client %s',
            self.id,
            self.client_info['address'],
        )
        self.gate = WorkerGate(
            self, name='session %i' % self.id, log_tag='worker', **kwargs
        )
        self.gate.start()
        logging.debug('New session %s', self.id)

    def destroy(self):
        logging.debug('Destroying session %s', self.id)
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
        return not self.active or self.get_age() > 3600

    def set_cookie(self, http_context):
        """
        Adds headers to :class:`aj.http.HttpContext` that set
        the session cookie
        """
        cookie = Cookie(
            'session',
            self.key,
            path='/',
            httponly=True
        ).render_response()
        http_context.add_header('Set-Cookie', cookie)
