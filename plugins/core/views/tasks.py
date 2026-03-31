import json
from jadi import component

from aj.api.http import get, post, HttpPlugin
from aj.api.endpoint import endpoint
from aj.plugins.core.api.tasks import TasksService


# This need to be more configurable, in order to allow custom user's plugins
ALLOWED_TASK_CLASSES = {
    'aj.plugins.plugins.tasks.InstallPlugin',
    'aj.plugins.plugins.tasks.UnInstallPlugin',
    'aj.plugins.plugins.tasks.UpgradeAll',
    'aj.plugins.filesystem.tasks.Transfer',
    'aj.plugins.filesystem.tasks.Delete',
    'aj.plugins.packages.tasks.UpdateLists',
}

@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.service = TasksService.get(self.context)

    @post('/api/core/tasks/start')
    @endpoint(api=True)
    def handle_api_tasks_start(self, http_context):
        data = json.loads(http_context.body.decode())
        cls_full_path = data['cls']
        if cls_full_path in ALLOWED_TASK_CLASSES:
            modulename, clsname = data['cls'].rsplit('.', 1)
            module = __import__(modulename, fromlist=[''])
            cls = getattr(module, clsname)
            task = cls(self.context, *data.get('args', []), **data.get('kwargs', {}))
            self.service.start(task)
            return task.id
        http_context.respond_forbidden()
        return ''

    @get('/api/core/tasks/request-update')
    @endpoint(api=True)
    def handle_api_tasks_request_update(self, http_context):
        self.service.send_update()
