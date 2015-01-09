from gevent.lock import RLock
import gevent.socket
from gevent.socket import wait_read, wait_write
import gipc
import logging
import time
import uuid


class GateStreamRequest (object):
    def __init__(self, object, endpoint):
        self.id = str(uuid.uuid4())
        self.object = object
        self.endpoint = endpoint

    def serialize(self):
        return {
            'id': self.id,
            'object': self.object,
        }

    @classmethod
    def deserialize(cls, data):
        self = cls(data['object'], None)
        self.id = data['id']
        return self


class GateStreamResponse (object):
    def __init__(self, id, object):
        self.id = id
        self.object = object

    def serialize(self):
        return {
            'id': self.id,
            'object': self.object,
        }

    @classmethod
    def deserialize(cls, data):
        self = cls(data['id'], data['object'])
        return self


class GateStreamServerEndpoint (object):
    def __init__(self, pipe):
        self.pipe = pipe
        self.buffer = {}
        self.buffer_lock = RLock()
        self.log = False

    def send(self, object):
        rq = GateStreamRequest(object, self)
        self.pipe.put(rq.serialize())
        if self.log:
            logging.debug('%s: >> %s' % (self, rq.id))
        return rq

    def buffer_single_response(self, timeout):
        try:
            with self.buffer_lock:
                try:
                    if timeout:
                        with gevent.Timeout(timeout) as t:
                            data = self.pipe.get(t)
                    else:
                        data = self.pipe.get()
                except gevent.Timeout:
                    return None
                except EOFError:
                    return None
                resp = GateStreamResponse.deserialize(data)
                if self.log:
                    logging.debug('%s: << %s' % (self, resp.id))
                self.buffer[resp.id] = resp
                return resp
        except IOError:
            return None

    def list_responses(self):
        with self.buffer_lock:
            return list(self.buffer)

    def has_response(self, id):
        with self.buffer_lock:
            return id in self.buffer

    def ack_response(self, id):
        with self.buffer_lock:
            return self.buffer.pop(id)


class GateStreamWorkerEndpoint (object):
    def __init__(self, pipe):
        self.pipe = pipe
        self.log = False

    def reply(self, request, object):
        resp = GateStreamResponse(request.id if request else None, object)
        self.pipe.put(resp.serialize())
        if self.log:
            logging.debug('%s: >> %s' % (self, resp.id))

    def recv(self):
        data = self.pipe.get()
        rq = GateStreamRequest.deserialize(data)
        if self.log:
            logging.debug('%s: << %s' % (self, rq.id))
        return rq
