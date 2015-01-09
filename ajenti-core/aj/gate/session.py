import uuid
import time
import logging
from cookies import Cookie, Cookies

from aj.gate.gate import WorkerGate


class Session (object):
    """
    Holds the HTTP session data
    """

    def __init__(self, key, client_info={}):
        self.id = uuid.uuid4()
        self.key = key
        self.client_info = client_info
        self.data = {}
        self.identity = None
        self.touch()
        self.active = True
        self.gate = WorkerGate(self)
        self.gate.start()
        logging.debug('New session %s' % self.id)

    def destroy(self):
        logging.debug('Destroying session %s' % self.id)
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

    def is_dead(self):
        return not self.active or (time.time() - self.timestamp) > 3600

    def set_cookie(self, http_context):
        """
        Adds headers to :class:`aj.http.HttpContext` that set the session cookie
        """
        http_context.add_header('Set-Cookie', Cookie('session', self.key, path='/', httponly=True).render_response())

