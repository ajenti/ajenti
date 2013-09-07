from ajenti.api import *
from ajenti.ipc import IPCHandler
from ajenti.plugins import manager

from api import TaskDefinition, JobDefinition


@plugin
class TaskManager (BasePlugin):
    classconfig_root = True
    default_classconfig = {
        'task_definitions': []
    }

    def init(self):
        self.task_definitions = [TaskDefinition(_) for _ in self.classconfig['task_definitions']]
        self.job_definitions = [JobDefinition(_) for _ in self.classconfig.get('job_definitions', [])]
        self.running_tasks = []

    def save(self):
        self.classconfig['task_definitions'] = [_.save() for _ in self.task_definitions]
        self.classconfig['job_definitions'] = [_.save() for _ in self.job_definitions]
        self.save_classconfig()

    def refresh(self):
        complete_tasks = [task for task in self.running_tasks if task.complete]
        for task in complete_tasks:
            self.running_tasks.remove(task)
    
    def run(self, task_definition=None, task_id=None):
        if task_id is not None:
            for td in self.task_definitions:
                if td.id == task_id:
                    task_definition = td
                    break
        if task_definition:
            task = task_definition.get_class().new(**task_definition.params)
            task.definition = task_definition
            self.running_tasks.append(task)
            task.start()


@plugin
class TasksIPC (IPCHandler):
    def init(self):
        self.manager = TaskManager.get(manager.context)
    
    def get_name(self):
        return 'tasks'

    def handle(self, args):
        command, task_id = args
        if command == 'run':
            self.manager.run(task_id=task_id)

        return ''
