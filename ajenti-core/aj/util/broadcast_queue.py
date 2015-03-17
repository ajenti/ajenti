import weakref
from gevent.queue import Queue


class BroadcastQueue(object):
    def __init__(self):
        self._queues = []

    def register(self):
        q = Queue()
        self._queues.append(weakref.ref(q))
        return q

    def broadcast(self, val):
        for q in list(self._queues):
            if q():
                q().put(val)
            else:
                self._queues.remove(q)
