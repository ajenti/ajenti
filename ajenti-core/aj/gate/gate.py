import gevent
import gipc
import greenlet
import logging
import os
import pickle
import signal

import aj
from aj.gate.stream import GateStreamServerEndpoint, GateStreamWorkerEndpoint
from aj.gate.worker import Worker
from aj.util import BroadcastQueue

class WorkerGate():
    def __init__(self, session, gateway_middleware, name=None, log_tag=None, restricted=False,
                 initial_identity=None):
        self.session = session
        self.process = None
        self.stream = None
        self.stream_reader = None
        self.worker = None
        self.name = name
        self.log_tag = log_tag
        self.restricted = restricted
        self.gateway_middleware = gateway_middleware
        self.initial_identity = initial_identity
        self.q_http_replies = BroadcastQueue()
        self.q_socket_messages = BroadcastQueue()

    def start(self):
        pipe_parent, pipe_child = gipc.pipe(
            duplex=True,
            encoder=lambda x: pickle.dumps(x, 2),
        )
        self.stream = GateStreamServerEndpoint(pipe_parent)
        stream_child = GateStreamWorkerEndpoint(pipe_child)

        self.process = gipc.start_process(
            target=self._target,
            kwargs={
                'stream': stream_child,
                '_pipe': pipe_child,
            }
        )

        logging.debug(f'Started child process {self.process.pid}')

        self.stream_reader = gevent.spawn(self._stream_reader)

    def stop(self):
        logging.debug(f'Stopping child process {self.process.pid}')

        try:
            os.killpg(self.process.pid, signal.SIGTERM)
        except OSError as e:
            logging.debug(f'Child process {self.process.pid} is already dead: {e}')
            return

        self.process.terminate()
        self.process.join(0.125)
        try:
            os.kill(self.process.pid, 0)
            logging.debug(f'Child process {self.process.pid} did not stop, killing')
            os.kill(self.process.pid, signal.SIGKILL)
            os.killpg(self.process.pid, signal.SIGKILL)

            os.kill(self.process.pid, 0)
            logging.error(f'Child process {self.process.pid} did not stop after SIGKILL!')
        except OSError:
            pass

        self.stream.destroy()
        self.stream_reader.kill(block=False)

    def send_config_data(self):
        logging.debug(f'Sending a config update to {self.name}')
        self.stream.send({
            'type': 'config-data',
            'data': {'config': aj.config.data, 'users': aj.users.data}
        })

    def send_sessionlist(self):
        logging.debug(f'Sending a session list update to {self.name}')
        self.stream.send({
            'type': 'session-list',
            'data': {key:session.serialize() for key,session in self.gateway_middleware.sessions.items()},
        })

    def _stream_reader(self):
        try:
            while True:
                resp = self.stream.buffer_single_response(None)
                if not resp:
                    return
                self.stream.ack_response(resp.id)
                if resp.object['type'] == 'socket':
                    self.q_socket_messages.broadcast(resp)
                if resp.object['type'] == 'http':
                    self.q_http_replies.broadcast(resp)
                if resp.object['type'] == 'terminate':
                    if self.session != self.gateway_middleware:
                        # Not the restricted session, we can disable it
                        self.session.deactivate()
                if resp.object['type'] == 'restart-master':
                    aj.restart()
                if resp.object['type'] == 'update-sessionlist':
                    self.gateway_middleware.broadcast_sessionlist()
                if resp.object['type'] == 'reload-config':
                    aj.config.load()
                    aj.users.load()
                    aj.config.ensure_structure()
                    self.gateway_middleware.broadcast_config_data()
                if resp.object['type'] == 'log':
                    method = {
                        'info': logging.info,
                        'warn': logging.warning,
                        'warning': logging.warning,
                        'debug': logging.debug,
                        'error': logging.error,
                        'critical': logging.critical,
                    }.get(resp.object['method'], None)
                    if method:
                        method(f"{resp.object['message']}", extra=resp.object['kwargs'])
        except greenlet.GreenletExit:
            pass

    def _target(self, stream=None, _pipe=None):
        self.worker = Worker(stream, self)
        self.worker.run()
