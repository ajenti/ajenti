from jadi import service
from aj.util import BroadcastQueue


@service
class Push(object):
    """
    A service providing push messages to the client.
    """
    def __init__(self, context):
        self.q = BroadcastQueue()

    def register(self):
        return self.q.register()

    def push(self, plugin, msg):
        """
        Sends a push message to the client.

        :param plugin: routing ID
        :param msg: message
        """
        self.q.broadcast((plugin, msg))
