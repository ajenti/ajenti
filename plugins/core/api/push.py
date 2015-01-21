from aj.api import *
from aj.util import BroadcastQueue


@service
class Push (object):
    def __init__(self, context):
        self.q = BroadcastQueue()

    def register(self):
        return self.q.register()

    def push(self, plugin, msg):
        self.q.broadcast((plugin, msg))
