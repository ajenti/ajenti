import json
from jadi import component

from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint
from aj.plugins.core.api.tasks import TasksService


@component(HttpPlugin)
class Handler(HttpPlugin):
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
        return task.id

    @url('/api/core/tasks/request-update')
    @endpoint(api=True)
    def handle_api_tasks_request_update(self, http_context):
        self.service.send_update()
