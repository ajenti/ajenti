from ajenti.api import *

from api import TaskDefinition


@plugin
class TaskManager (BasePlugin):
    classconfig_root = True
    default_classconfig = {
        'task_definitions': []
    }

    def init(self):
        self.task_definitions = [TaskDefinition(_) for _ in self.classconfig['task_definitions']]

    def save(self):
        self.classconfig['task_definitions'] = [_.save() for _ in self.task_definitions]
        self.save_classconfig()

        
