import gevent

from aj.api import *
from aj.api.http import SocketEndpoint
from aj.plugins.core.api.tasks import TasksService


@component(SocketEndpoint)
class TasksSocket (SocketEndpoint):
    plugin = 'tasks'

    def __init__(self, context):
        SocketEndpoint.__init__(self, context)
        self.service = TasksService.get(self.context)

    def on_connect(self, message, *args):
        # todo: spawn in namespace
        self.reader = gevent.spawn(self._reader)

    def on_message(self, message, *args):
        if message == 'request-update':
            self.send_update()

    def _reader(self):
        q = self.service.notifications.register()
        while True:
            try:
                msg = q.get()
            except:
                return
            if msg:
                self.send({
                    'type': 'message',
                    'message': msg,
                })
            self.send_update()

    def send_update(self):
        self.send({
            'type': 'update',
            'tasks': self.format_tasks(),
        })

    def format_tasks(self):
        return [
            {
                'id': task.id,
                'name': task.name,
                'running': task.running,
                'started': task.started,
                'finished': task.finished,
                'progress': task.progress,
                'exception': task.exception,
            }
            for task in sorted(self.service.tasks.values(), key=lambda x: -x.started)
        ]
