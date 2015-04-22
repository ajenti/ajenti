import gevent.queue
from jadi import component

from aj.api.http import SocketEndpoint
from aj.plugins.core.api.push import Push


@component(SocketEndpoint)
class PushSocket(SocketEndpoint):
    plugin = 'push'

    def __init__(self, context):
        SocketEndpoint.__init__(self, context)

    def on_connect(self, message, *args):
        self.spawn(self._reader)

    def _reader(self):
        q = Push.get(self.context).register()
        while True:
            try:
                plugin, msg = q.get()
            except gevent.queue.Empty:
                return
            except EOFError:
                return
            if msg:
                self.send({
                    'plugin': plugin,
                    'message': msg,
                })
