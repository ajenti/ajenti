import hashlib
import logging
import os
import pwd
import random
import time
import gevent
from socketio import Namespace
from cookies import Cookies
from gevent.timeout import Timeout
from jadi import service

import aj
from aj.gate.gate import WorkerGate
from aj.gate.session import Session
from aj.gate.worker import WorkerError
from aj.util import str_fsize

class SocketIOQueue():
    def __init__(self, sid, gate, namespace):
        self.sid = sid
        self.gate = gate
        self.namespace = namespace
        self.queue = self.gate.q_socket_messages.register()
        gevent.spawn(self._stream_reader)

    def _stream_reader(self):
        while True:
            resp = self.queue.get()
            self.namespace.emit('message', resp.object['message'], room=self.sid)

class SocketIONamespace(Namespace):

    def __init__(self, context):
        Namespace.__init__(self, namespace="/socket")
        self.context = context

    def _send_worker_event(self, sid, event, message=None):
        gate = self.get_session(sid).get('gate', None)
        if gate:
            gate.stream.send({
                'type': 'socket',
                'event': event,
                'namespace': id(self),
                'message': message,
            })

    def on_connect(self, sid, environ):
        logging.debug(f'Socket {id(self)} connected')
        session = GateMiddleware.get(self.context).obtain_session(environ)
        if session:
            queue = SocketIOQueue(sid, session.gate, self)
            self.save_session(sid, {'gate': session.gate, 'queue': queue})
            self._send_worker_event(sid, 'connect')

    def on_disconnect(self, sid):
        logging.debug(f'Socket {id(self)} disconnected')
        self._send_worker_event(sid, 'disconnect')
        self.disconnect(sid)

    def on_message(self, sid, message):
        logging.debug(f'Socket {id(self)} message: {repr(message)}')
        self._send_worker_event(sid, 'message', message)

@service
class GateMiddleware():
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
        return hashlib.sha256(h.encode('utf-8')).hexdigest()

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
            logging.info(f"Closing session {victim.id} due to pool overflow")
            victim.deactivate()
            self.vacuum()

        client_info = {
            'address': env.get('REMOTE_ADDR', None),
        }
        session_key = self.generate_session_key(env)
        session_max_time = aj.config.data['session_max_time']
        session = Session(session_key, gateway_middleware=self, client_info=client_info, session_max_time=session_max_time, **kwargs)
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

    def broadcast_sessionlist(self):
        self.restricted_gate.send_sessionlist()
        for session in self.sessions.values():
            if not session.is_dead():
                session.gate.send_sessionlist()

    def handle(self, http_context):
        start_time = time.time()

        self.vacuum()

        session = self.obtain_session(http_context.env)
        gate = None

        if not session and aj.dev_autologin:
            username = pwd.getpwuid(os.geteuid()).pw_name
            logging.warning(f'Opening an autologin session for user {username}')
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
            return [b'Worker timeout']

        # ---

        if 'error' in resp.object:
            raise WorkerError(resp.object)

        for header in resp.object['headers']:
            http_context.add_header(*header)

        headers = dict(resp.object['headers'])
        if 'X-Session-Redirect' in headers:
            # new authenticated session
            username = headers['X-Session-Redirect']
            logging.info(f'Opening a session for user {username}')
            session = self.open_session(
                http_context.env,
                initial_identity=username,
                auth_info=headers['X-Auth-Info'],
            )
            session.set_cookie(http_context)

        http_context.respond(resp.object['status'])
        content = resp.object['content']

        end_time = time.time()
        duration = end_time - start_time
        size = str_fsize(len(content[0] if content else []))
        status = str(http_context.status).split()[0]
        logging.debug(
                f'{duration:.3f} {size:>12}'
                f'   {status} {http_context.env["REQUEST_METHOD"]} {http_context.path}'
        )

        for index, item in enumerate(content):
            if isinstance(item, str):
                content[index] = item.encode('utf-8')

        # Touch the session in case system time has dramatically
        # changed during request
        if session:
            session.touch()

        return content
