from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.plugins import manager
from ajenti.ui import on
from ajenti.ui.binder import Binder, DictAutoBinding

from api import Task, TaskDefinition, JobDefinition
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

        def post_td_bind(object, collection, item, ui):
            if item.get_class():
                params_ui = self.ui.inflate(item.get_class().ui)
                item.binder = DictAutoBinding(item, 'params', params_ui.find('bind'))
                item.binder.populate()
                ui.find('slot').empty()
                ui.find('slot').append(params_ui)

        def post_td_update(object, collection, item, ui):
            if hasattr(item, 'binder'):
                item.binder.update()

        def post_rt_bind(object, collection, item, ui):
            def abort():
                item.abort()
                self.refresh()
            ui.find('abort').on('click', abort)
        
        self.find('task_definitions').post_item_bind = post_td_bind
        self.find('task_definitions').post_item_update = post_td_update
        self.find('running_tasks').post_item_bind = post_rt_bind
        
        self.find('job_definitions').new_item = lambda c: JobDefinition()

    def on_page_load(self):
        self.refresh()

    @on('refresh', 'click')
    def refresh(self):
        self.binder.reset(self.manager)
        self.manager.refresh()

        dd = self.find('task-classes')
        dd.labels = []
        dd.values = []
        for task in Task.get_classes():
            if not task.hidden:
                dd.labels.append(task.name)
                dd.values.append(task.classname)

        dd = self.find('task-selector')
        dd.labels = [_.name for _ in self.manager.task_definitions]
        dd.values = [_.id for _ in self.manager.task_definitions]
        self.find('run-task-selector').labels = dd.labels
        self.find('run-task-selector').values = dd.values

        self.binder.autodiscover().populate()

    @on('run-task', 'click')
    def on_run_task(self):
        self.manager.run(task_id=self.find('run-task-selector').value, context=self.context)
        self.refresh()

    @on('create-task', 'click')
    def on_create_task(self):
        cls = self.find('task-classes').value
        td = TaskDefinition(task_class=cls)
        td.name = td.get_class().name
        self.manager.task_definitions.append(td)
        self.refresh()

    @on('save', 'click')
    def on_save(self):
        self.binder.update()
        self.manager.save()
        self.refresh()
