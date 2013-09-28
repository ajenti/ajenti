import logging
import threading
import uuid

from ajenti.api import *


class TaskResult (object):
    SUCCESS = 0
    ABORTED = 1
    ERROR = 2
    CRASH = 3

    def __init__(self):
        self.result = TaskResult.SUCCESS
        self.output = ''
        self.name = None


class TaskError (Exception):
    pass


@interface
class Task (object):
    """
    Base class for custom tasks
    
    :param name: display name
    :param ui: full layout name for parameter editor, will be bound to parameter dictionary (so begin it with <bind:dict bind="params">)
    :param hidden: if True, task won't be available for manual creation
    """

    name = '---'
    ui = None
    hidden = False

    def __init__(self, **kwargs):
        self.params = kwargs

    def init(self):
        self._progress = 0
        self._progress_max = 1
        self.running = False
        self.complete = False
        self.pending = False
        self.aborted = False
        self.parallel = False
        self.message = ''
        self.result = TaskResult()
        self.callback = lambda x: None

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        logging.info('Starting task %s' % self.__class__.__name__)
        self.running = True
        self.result.name = self.name
        try:
            self.run(**self.params)
            self.result.result = TaskResult.SUCCESS
        except TaskError, e:
            self.result.result = TaskResult.ERROR
            self.result.output = e.message
        except Exception, e:
            self.result.result = TaskResult.CRASH
            self.result.output = str(e)
            logging.exception(str(e))
        self.running = False
        self.complete = True 
        logging.info('Task %s complete (%s)' % (self.__class__.__name__, 'aborted' if self.aborted else 'success'))
        self.callback(self)

    def run(**kwargs):
        """
        Override with your task actions here.
        Raise :class:`TaskError` in case of emergency.
        Check `aborted` often and return if it's True

        :param **kwargs: saved task parameters
        """

    def abort(self):
        if not self.running:
            return
        self.aborted = True
        self.result.result = TaskResult.ABORTED
        self.thread.join()
        
    def set_progress(self, current, max):
        self._progress, self._progress_max = current, max

    def get_progress(self):
        return self._progress, self._progress_max


class TaskDefinition (object):
    def __init__(self, j={}, task_class=None):
        self.name = j.get('name', 'unnamed')
        self.parallel = j.get('parallel', False)
        self.task_class = j.get('task_class', task_class)
        self.params = j.get('params', self.get_class().default_params if self.get_class() else {})
        self.id = j.get('id', str(uuid.uuid4()))

    def get_class(self):
        for task in Task.get_classes():
            if task.classname == self.task_class:
                return task

    def save(self):
        return {
            'name': self.name,
            'task_class': self.task_class,
            'params': self.params,
            'id': self.id,
        }


class JobDefinition (object):
    def __init__(self, j={}):
        self.name = j.get('name', 'unnamed')
        self.task_id = j.get('task_id', None)
        self.id = j.get('id', str(uuid.uuid4()))
        self.schedule_special = j.get('schedule_special', None)
        self.schedule_minute = j.get('schedule_minute', '0')
        for _ in ['hour', 'day_of_month', 'month', 'day_of_week']:
            setattr(self, 'schedule_' + _, j.get('schedule_' + _, '*'))

    def save(self):
        return {
            'name': self.name,
            'task_id': self.task_id,
            'id': self.id,
            'schedule_special': self.schedule_special,
            'schedule_minute': self.schedule_minute,
            'schedule_hour': self.schedule_hour,
            'schedule_day_of_month': self.schedule_day_of_month,
            'schedule_month': self.schedule_month,
            'schedule_day_of_week': self.schedule_day_of_week,
        }
