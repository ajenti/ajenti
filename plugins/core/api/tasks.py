import gevent
import gevent.queue
import gipc
import logging
import os
import setproctitle
import sys
import time
import traceback
from jadi import service

from aj.log import set_log_params, init_log_forwarding
from aj.util import BroadcastQueue
from aj.plugins.core.api.push import Push


class Task(object):
    """
    Tasks are one-off child processes with progress reporting. This is a base abstract class.
    """

    name = None
    """Display name"""

    def __init__(self, context, *args, **kwargs):
        self.context = context
        self.running = False
        self.exception = None
        self.started = time.time()
        self.finished = None
        self.id = os.urandom(32).encode('hex')
        self.reader = None
        self.pipe = None
        self.process = None
        self.service = TasksService.get(self.context)
        self.progress = {
            'message': None,
            'done': None,
            'total': None,
        }

    def start(self):
        """
        Starts the task's process
        """
        self.pipe, pipe_child = gipc.pipe(duplex=True)
        self.running = True
        self.process = gipc.start_process(
            target=self._worker,
            kwargs={
                'pipe': pipe_child,
            }
        )
        self.reader = gevent.spawn(self._reader)

    def abort(self):
        self.process.terminate()

    def report_progress(self, message=None, done=None, total=None):
        """
        Updates the task's process info.

        :param message: text message
        :param done: number of processed items
        :param total: total number of items
        """
        self.progress['message'] = message
        self.progress['done'] = done
        self.progress['total'] = total
        self.pipe.put({
            'type': 'progress',
            'progress': self.progress,
        })

    def _worker(self, pipe=None):
        self.pipe = pipe
        setproctitle.setproctitle(
            '%s task %s #%i' % (
                sys.argv[0],
                self.__class__.__name__,
                os.getpid()
            )
        )
        set_log_params(tag='task')
        init_log_forwarding(self.send_log_event)
        logging.info('Starting task %s (%s)', self.id, self.__class__.__name__)
        try:
            self.run()
            self.pipe.put({'type': 'done'})
        # pylint: disable=W0703
        except Exception as e:
            logging.error('Exception in task %s', self.id)
            logging.error(str(e))
            traceback.print_exc()
            self.pipe.put({'type': 'exception', 'exception': str(e)})
        logging.info('Task %s finished', self.id)

    def _reader(self):
        while True:
            try:
                msg = self.pipe.get()
            except EOFError:
                self.running = False
                self.finished = time.time()
                logging.debug('Task %s pipe was closed', self.id)
                self.service.remove(self.id)
                self.service.notify()
                return
            if msg['type'] == 'exception':
                self.exception = msg['exception']
                logging.debug('Task %s reports exception: %s', self.id, msg['exception'])
                self.service.notify({
                    'type': 'exception',
                    'exception': self.exception,
                    'task': {
                        'id': self.id,
                        'name': self.name,
                    }
                })
                self.service.remove(self.id)
                self.service.notify()
            if msg['type'] == 'progress':
                self.progress = msg['progress']
                logging.debug(
                    'Task %s reports progress: %s %s/%s',
                    self.id,
                    self.progress['message'],
                    self.progress['done'],
                    self.progress['total'],
                )
            if msg['type'] == 'done':
                logging.debug('Task %s reports completion', self.id)
                self.service.notify({
                    'type': 'done',
                    'task': {
                        'id': self.id,
                        'name': self.name,
                    }
                })
                self.service.remove(self.id)
                self.service.notify()
            if msg['type'] == 'push':
                Push.get(self.context).push(msg['plugin'], msg['message'])
                logging.debug(
                    'Task %s sends a push message: %s %s',
                    self.id,
                    msg['plugin'],
                    msg['message'],
                )
            if msg['type'] == 'log':
                self.context.worker.send_to_upstream(msg)
            self.service.notify()

    def run(self):
        """
        Override this with your task's logic.
        """
        raise NotImplementedError

    def push(self, plugin, message):
        """
        An interface to :class:`aj.plugins.core.api.push.Push` usable from inside the task's process
        """
        self.pipe.put({
            'type': 'push',
            'plugin': plugin,
            'message': message,
        })

    def send_log_event(self, method, message, *args, **kwargs):
        self.pipe.put({
            'type': 'log',
            'method': method,
            'message': message % args,
            'kwargs': kwargs,
        })


@service
class TasksService(object):
    def __init__(self, context):
        self.context = context
        self.tasks = {}
        self.notifications = BroadcastQueue()

    def start(self, task):
        self.tasks[task.id] = task
        task.start()
        self.send_update()

    def abort(self, _id):
        self.tasks[_id].abort()

    def remove(self, _id):
        if _id in self.tasks:
            self.tasks.pop(_id)

    def notify(self, message=None):
        if message:
            Push.get(self.context).push(
                'tasks', {
                    'type': 'message',
                    'message': message,
                }
            )
        self.send_update()

    def send_update(self):
        Push.get(self.context).push(
            'tasks', {
                'type': 'update',
                'tasks': self.format_tasks(),
            }
        )

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
            for task in sorted(self.tasks.values(), key=lambda x: x.started)
        ]
