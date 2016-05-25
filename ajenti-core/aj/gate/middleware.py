import hashlib
import logging
import os
import pwd
import random
import six
import socketio
import time
from cookies import Cookies
from gevent.timeout import Timeout
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from jadi import service

import aj
from aj.api.http import BaseHttpHandler
from aj.gate.gate import WorkerGate
from aj.gate.session import Session
from aj.gate.worker import WorkerError
from aj.util import str_fsize


class SocketIONamespace(BaseNamespace, BroadcastMixin):
    name = '/socket'
    """ Endpoint ID """

    def __init__(self, context, env, *args, **kwargs):
        BaseNamespace.__init__(self, env, *args, **kwargs)
        BroadcastMixin.__init__(self)
        self.context = context
        self.env = env
        self.gate = None

    def get_initial_acl(self):
        return ['recv_connect']

    def _stream_reader(self):
        q = self.gate.q_socket_messages.register()
        while True:
            resp = q.get()
            self.emit('message', resp.object['message'])

    def _send_worker_event(self, event, message=None):
        if self.gate:
            self.gate.stream.send({
                'type': 'socket',
                'event': event,
                'namespace': id(self),
                'message': message,
            })

    def recv_connect(self):
        logging.debug('Socket %s connected', id(self))
        session = GateMiddleware.get(self.context).obtain_session(self.env)
        if session:
            self.gate = session.gate
            self.spawn(self._stream_reader)
            self.add_acl_method('on_message')
            self.add_acl_method('recv_message')
            self.add_acl_method('recv_disconnect')
            self._send_worker_event('connect')

    def recv_disconnect(self):
        logging.debug('Socket %s disconnected', id(self))
        self._send_worker_event('disconnect')
        self.disconnect(silent=True)

    def on_message(self, message, *args):
        logging.debug('Socket %s message: %s', id(self), repr(message))
        self._send_worker_event('message', message)


@service
class SocketIORouteHandler(BaseHttpHandler):
    def __init__(self, context):
        self.namespaces = {
            '/socket': lambda *args, **kwargs: SocketIONamespace(
                context, *args, **kwargs
            )
        }

    def handle(self, context):
        return six.binary_type(socketio.socketio_manage(
            context.env, self.namespaces, context
        ) or b'')


@service
class GateMiddleware(object):
    def __init__(self, context):
        self.context = context
        self.sessions = {}
        self.restricted_gate = WorkerGate(
            self,
            gateway_middleware=self,
            restricted=True,
            name='restricted session',
            log_tag='restricted'
        )
        self.restricted_gate.start()

    def generate_session_key(self, env):
        h = str(random.random())
        h += env.get('REMOTE_ADDR', '')
        h += env.get('HTTP_USER_AGENT', '')
        h += env.get('HTTP_HOST', '')
        return hashlib.sha1(h.encode('utf-8')).hexdigest()

    def vacuum(self):
        """
        Eliminates dead sessions
        """
        for session in [x for x in self.sessions.values() if x.is_dead()]:
            session.destroy()
            if session.key in self.sessions:
                del self.sessions[session.key]

    def destroy(self):
        for session in self.sessions.values():
            session.deactivate()
        self.vacuum()

    def open_session(self, env, **kwargs):
        """
        Creates a new session for the :class:`aj.http.HttpContext`
        """
        max_sessions = aj.config.data['max_sessions']
        if max_sessions and len(self.sessions) >= max_sessions:
            candidates = sorted(self.sessions.keys(), key=lambda k: -self.sessions[k].get_age())
            victim = self.sessions[candidates[0]]
            logging.info("Closing session %s due to pool overflow" % victim.id)
            victim.deactivate()
            self.vacuum()

        client_info = {
            'address': env.get('REMOTE_ADDR', None),
        }
        session_key = self.generate_session_key(env)
        session = Session(session_key, gateway_middleware=self, client_info=client_info, **kwargs)
        self.sessions[session_key] = session
        return session

    def obtain_session(self, env):
        cookie_str = env.get('HTTP_COOKIE', None)
        session = None
        if cookie_str:
            cookie = Cookies.from_request(
                cookie_str,
                ignore_bad_cookies=True,
            ).get('session', None)
            if cookie and cookie.value:
                if cookie.value in self.sessions:
                    # Session found
                    session = self.sessions[cookie.value]
                    if session.is_dead():
                        session = None
        return session

    def broadcast_config_data(self):
        self.restricted_gate.send_config_data()
        for session in self.sessions.values():
            if not session.is_dead():
                session.gate.send_config_data()

    def handle(self, http_context):
        start_time = time.time()

        self.vacuum()

        session = self.obtain_session(http_context.env)
        gate = None

        if not session and aj.dev_autologin:
            username = pwd.getpwuid(os.geteuid()).pw_name
            logging.warn('Opening an autologin session for user %s', username)
            session = self.open_session(
                http_context.env,
                initial_identity=username
            )
            session.set_cookie(http_context)

        if session:
            session.touch()
            gate = session.gate
        else:
            gate = self.restricted_gate

        if http_context.path.startswith('/socket'):
            http_context.fallthrough(SocketIORouteHandler.get(self.context))
            http_context.respond_ok()
            return 'Socket closed'

        request_object = {
            'type': 'http',
            'context': http_context.serialize(),
        }

        # await response

        try:
            timeout = 600
            with Timeout(timeout) as t:
                q = gate.q_http_replies.register()
                rq = gate.stream.send(request_object)
                while True:
                    resp = q.get(t)
                    if resp.id == rq.id:
                        break
        # pylint: disable=E0712
        except Timeout:
            http_context.respond('504 Gateway Timeout')
            return 'Worker timeout'

        # ---

        if 'error' in resp.object:
            raise WorkerError(resp.object)

        for header in resp.object['headers']:
            http_context.add_header(*header)

        headers = dict(resp.object['headers'])
        if 'X-Session-Redirect' in headers:
            # new authenticated session
            username = headers['X-Session-Redirect']
            logging.info('Opening a session for user %s', username)
            session = self.open_session(
                http_context.env,
                initial_identity=username,
                auth_info=headers['X-Auth-Info'],
            )
            session.set_cookie(http_context)

        http_context.respond(resp.object['status'])
        content = resp.object['content']

        end_time = time.time()
        logging.debug(
            '%.03fs %12s   %s %s %s',
            end_time - start_time,
            str_fsize(len(content[0] if content else [])),
            str(http_context.status).split()[0],
            http_context.env['REQUEST_METHOD'],
            http_context.path
        )

        for index, item in enumerate(content):
            if isinstance(item, six.text_type):
                content[index] = item.encode('utf-8')

        # Touch the session in case system time has dramatically
        # changed during request
        if session:
            session.touch()

        return content
