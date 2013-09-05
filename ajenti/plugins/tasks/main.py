from ajenti.plugins import manager

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from api import Task, TaskDefinition
from manager import TaskManager


@plugin
class Tasks (SectionPlugin):
    def init(self):
        self.title = _('Tasks')
        self.icon = 'cog'
        self.category = _('Tools')

        self.append(self.ui.inflate('tasks:main'))

        self.manager = TaskManager.get(manager.context)
        self.binder = Binder(None, self)

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.binder.reset(self.manager)

        dd = self.find('task-classes')
        dd.labels = []
        dd.values = []
        for task in Task.get_classes():
            dd.labels.append(task.name)
            dd.values.append(task.classname)

        self.binder.autodiscover().populate()

    @on('create-task', 'click')
    def on_create_task(self):
        cls = self.find('task-classes').value
        td = TaskDefinition()
        td.task_class = cls
        self.manager.task_definitions.append(td)
        self.refresh()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        self.manager.save()
        self.refresh()
