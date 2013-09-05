from ajenti.api import *


@interface
class Task (object):
    name = '---'

    def init(self):
        self._progress = 0
        self._progress_max = 1

    def run():
        pass
        
    def set_progress(self, current, max):
        self._progress, self._progress_max = current, max

    def get_progress(self):
        return self._progress, self._progress_max


class TaskDefinition (object):
    def __init__(self, j={}):
        self.name = j.get('name', 'unnamed')
        self.task_class = j.get('task_class', None)

    def save(self):
        return {
            'name': self.name,
            'task_class': self.task_class,
        }


@plugin
class TestTask (Task):
    name = 'Test'
    
    def run(self):
        print 'run'


