import gevent
import json

from aj.api import *
from aj.api.http import SocketEndpoint, BaseHttpHandler, url, HttpPlugin
from aj.plugins.core.api.endpoint import endpoint
from aj.plugins.core.api.tasks import TasksService


@component(HttpPlugin)
class Handler (HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.service = TasksService.get(self.context)

    @url('/api/core/tasks/start')
    @endpoint(api=True)
    def handle_api_tasks_start(self, http_context):
        data = json.loads(http_context.body)
        modulename, clsname = data['cls'].rsplit('.', 1)
        module = __import__(modulename, fromlist=[''])
        cls = getattr(module, clsname)
        task = cls(self.context, *data.get('args', []), **data.get('kwargs', {}))
        self.service.start(task)


@component(SocketEndpoint)
class TasksSocket (SocketEndpoint):
    plugin = 'tasks'

    def __init__(self, context):
        SocketEndpoint.__init__(self, context)
        self.service = TasksService.get(self.context)

    def on_connect(self, message, *args):
        self.reader = self.spawn(self._reader)

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
                print self, msg
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
            for task in sorted(self.service.tasks.values(), key=lambda x: x.started)
        ]
