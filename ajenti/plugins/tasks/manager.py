from datetime import datetime

from ajenti.api import *
from ajenti.ipc import IPCHandler
from ajenti.plugins import manager

from api import TaskDefinition, JobDefinition
from ajenti.plugins.cron.api import CronManager
from reconfigure.items.crontab import CrontabNormalTaskData, CrontabSpecialTaskData


@plugin
@rootcontext
class TaskManager (BasePlugin):
    classconfig_root = True
    default_classconfig = {
        'task_definitions': []
    }

    def init(self):
        self.task_definitions = [TaskDefinition(_) for _ in self.classconfig['task_definitions']]
        self.job_definitions = [JobDefinition(_) for _ in self.classconfig.get('job_definitions', [])]
        self.running_tasks = []
        self.pending_tasks = []
        self.result_log = []

    @property
    def all_tasks(self):
        return self.running_tasks + self.pending_tasks

    def save(self):
        self.classconfig['task_definitions'] = [_.save() for _ in self.task_definitions]
        self.classconfig['job_definitions'] = [_.save() for _ in self.job_definitions]
        self.save_classconfig()

        prefix = 'ajenti-ipc tasks run '

        tab = CronManager.get().load_tab('root')
        for item in list(tab.tree.normal_tasks):
            if item.command.startswith(prefix):
                tab.tree.normal_tasks.remove(item)
        for item in list(tab.tree.special_tasks):
            if item.command.startswith(prefix):
                tab.tree.special_tasks.remove(item)

        for job in self.job_definitions:
            if job.schedule_special:
                e = CrontabSpecialTaskData()
                e.special = job.schedule_special
                e.command = prefix + job.task_id
                tab.tree.special_tasks.append(e)
            else:
                e = CrontabNormalTaskData()
                e.minute = job.schedule_minute
                e.hour = job.schedule_hour
                e.day_of_month = job.schedule_day_of_month
                e.month = job.schedule_month
                e.day_of_week = job.schedule_day_of_week
                e.command = prefix + job.task_id
                tab.tree.normal_tasks.append(e)

        CronManager.get().save_tab('root', tab)

    def task_done(self, task):
        task.time_completed = datetime.now()
        task.result.time_started = task.time_started
        task.result.duration = task.time_completed - task.time_started
        if task.execution_context:
            task.execution_context.notify('info', _('Task %s finished') % task.name)
        if task in self.running_tasks:
            self.result_log = [task.result] + self.result_log[:9]
            self.running_tasks.remove(task)
        if not self.running_tasks:
            if self.pending_tasks:
                t = self.pending_tasks.pop(0)
                self.run(task=t)

    def refresh(self):
        complete_tasks = [task for task in self.running_tasks if task.complete]
        for task in complete_tasks:
            self.running_tasks.remove(task)

    def run(self, task=None, task_definition=None, task_id=None, context=None):
        if task_id is not None:
            for td in self.task_definitions:
                if td.id == task_id:
                    task_definition = td
                    break
            else:
                raise IndexError('Task not found')

        if task_definition is not None:
            task = task_definition.get_class().new(**task_definition.params)
            task.definition = task_definition
            task.parallel = task_definition.parallel

        task.time_started = datetime.now()
        task.execution_context = context

        if not task.parallel and self.running_tasks:
            self.pending_tasks.append(task)
            task.pending = True
            if task.execution_context:
                task.execution_context.notify('info', _('Task %s queued') % task.name)
        else:
            self.running_tasks.append(task)
            task.pending = False

            old_callback = task.callback
            def new_callback(task):
                old_callback(task)
                self.task_done(task)
            task.callback = new_callback

            if task.execution_context:
                task.execution_context.notify('info', _('Task %s started') % task.name)
            task.start()


@plugin
class TasksIPC (IPCHandler):
    def init(self):
        self.manager = TaskManager.get()

    def get_name(self):
        return 'tasks'

    def handle(self, args):
        command, task_id = args
        if command == 'run':
            self.manager.run(task_id=task_id)

        return ''
