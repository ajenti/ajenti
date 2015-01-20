import gipc
import greenlet
import logging
import os
import signal

from aj.gate.stream import *
from aj.gate.worker import *
from aj.util import BroadcastQueue


class WorkerGate (object):
    def __init__(self, session):
        self.session = session
        self.process = None
        self.q_http_replies = BroadcastQueue()
        self.q_socket_messages = BroadcastQueue()

    def start(self):
        pipe_parent, pipe_child = gipc.pipe(duplex=True)
        self.stream = GateStreamServerEndpoint(pipe_parent)
        stream_child = GateStreamWorkerEndpoint(pipe_child)

        self.process = gipc.start_process(
            target=self._target,
            kwargs={
                'stream': stream_child,
                '_pipe': pipe_child,
            }
        )

        logging.debug('Started child process %s' % self.process.pid)

        self.stream_reader = gevent.spawn(self._stream_reader)

    def stop(self):
        logging.debug('Stopping child process %s' % self.process.pid)

        try:
            os.killpg(self.process.pid, signal.SIGTERM)
        except OSError as e:
            logging.debug('Child process %s is already dead: %s' % (self.process.pid, e))
            return

        self.process.terminate()
        self.process.join(0.125)
        try:
            os.kill(self.process.pid, 0)
            logging.debug('Child process %s did not stop, killing' % self.process.pid)
            os.kill(self.process.pid, signal.SIGKILL)
            os.killpg(self.process.pid, signal.SIGKILL)
            try:
                os.kill(self.process.pid, 0)
                logging.error('Child process %s did not stop after SIGKILL!' % self.process.pid)
            except OSError:
                pass
        except OSError:
            pass

        self.stream_reader.kill(block=False)

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
                    self.session.deactivate()
        except greenlet.GreenletExit:
            pass

    def _target(self, stream=None, _pipe=None):
        self.worker = Worker(stream, self)
        self.worker.run()
