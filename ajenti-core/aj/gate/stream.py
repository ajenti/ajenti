from gevent.lock import RLock
import binascii
import gevent.socket
import os
import logging


class GateStreamRequest(object):
    def __init__(self, obj, endpoint):
        self.id = binascii.hexlify(os.urandom(32))
        self.object = obj
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


class GateStreamResponse(object):
    def __init__(self, _id, obj):
        self.id = _id
        self.object = obj

    def serialize(self):
        return {
            'id': self.id,
            'object': self.object,
        }

    @classmethod
    def deserialize(cls, data):
        self = cls(data['id'], data['object'])
        return self


class GateStreamServerEndpoint(object):
    def __init__(self, pipe):
        self.pipe = pipe
        self.buffer = {}
        self.buffer_lock = RLock()
        self.log = False

    def send(self, obj):
        rq = GateStreamRequest(obj, self)
        self.pipe.put(rq.serialize())
        if self.log:
            logging.debug('%s: >> %s', self, rq.id)
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
                # pylint: disable=E0712
                except gevent.Timeout:
                    return None
                except EOFError:
                    return None
                resp = GateStreamResponse.deserialize(data)
                if self.log:
                    logging.debug('%s: << %s', self, resp.id)
                self.buffer[resp.id] = resp
                return resp
        except IOError:
            return None

    def list_responses(self):
        with self.buffer_lock:
            return list(self.buffer)

    def has_response(self, _id):
        with self.buffer_lock:
            return _id in self.buffer

    def ack_response(self, _id):
        with self.buffer_lock:
            return self.buffer.pop(_id)


class GateStreamWorkerEndpoint(object):
    def __init__(self, pipe):
        self.pipe = pipe
        self.log = False

    def reply(self, request, obj):
        resp = GateStreamResponse(request.id if request else None, obj)
        self.pipe.put(resp.serialize())
        if self.log:
            logging.debug('%s: >> %s', self, resp.id)

    def recv(self):
        data = self.pipe.get()
        rq = GateStreamRequest.deserialize(data)
        if self.log:
            logging.debug('%s: << %s', self, rq.id)
        return rq
