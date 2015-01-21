import gipc
import logging
import sys
import gevent
import time
import traceback
import os
import setproctitle
import signal
import uuid

from aj.api import *
from aj.log import set_log_params
from aj.util import BroadcastQueue
from aj.plugins.core.api.push import Push


class Task (object):
    name = None

    def __init__(self, context):
        self.context = context
        self.running = False
        self.exception = None
        self.started = time.time()
        self.finished = None
        self.id = str(uuid.uuid4())
        self.reader = None
        self.service = TasksService.get(self.context)
        self.progress = {
            'message': None,
            'done': None,
            'total': None,
        }

    def _start(self):
        self.pipe, pipe_child = gipc.pipe(duplex=True)
        self.running = True
        self.process = gipc.start_process(
            target=self._worker,
            kwargs={
                'pipe': pipe_child,
            }
        )
        self.reader = gevent.spawn(self._reader)

    def _abort(self):
        self.greenlet.kill(block=False)

    def report_progress(self, message=None, done=None, total=None):
        self.progress['message'] = message
        self.progress['done'] = done
        self.progress['total'] = total
        self.pipe.put({
            'type': 'progress',
            'progress': self.progress,
        })

    def _worker(self, pipe=None):
        self.pipe = pipe
        setproctitle.setproctitle('%s task %s #%i' % (sys.argv[0], self.__class__.__name__, os.getpid()))
        set_log_params(tag='task')
        logging.info('Starting task %s (%s)' % (self.id, self.__class__.__name__))
        try:
            self.run()
        except Exception as e:
            logging.error('Exception in task %s' % self.id)
            logging.error(str(e))
            traceback.print_exc()
            self.pipe.put({'type': 'exception', 'exception': str(e)})
        self.pipe.put({'type': 'done'})
        logging.info('Task %s finished' % self.id)

    def _reader(self):
        while True:
            try:
                msg = self.pipe.get()
            except:
                self.running = False
                self.finished = time.time()
                logging.debug('Task %s pipe was closed' % self.id)
                self.service.remove(self.id)
                self.service.notify()
                return
            #print '<<', msg
            if msg['type'] == 'exception':
                self.exception = msg['exception']
                logging.debug('Task %s reports exception: %s' % (self.id, msg['exception']))
                self.service.notify({
                    'type': 'exception',
                    'exception': self.exception,
                    'task': {
                        'id': self.id,
                        'name': self.name,
                    }
                })
            if msg['type'] == 'progress':
                self.progress = msg['progress']
                logging.debug('Task %s reports progress: %s %s/%s' % (
                    self.id, self.progress['message'], self.progress['done'], self.progress['total'],
                ))
            if msg['type'] == 'done':
                logging.debug('Task %s reports completion' % self.id)
                self.service.notify({
                    'type': 'done',
                    'task': {
                        'id': self.id,
                        'name': self.name,
                    }
                })
            if msg['type'] == 'push':
                Push.get(self.context).push(msg['plugin'], msg['message'])
                logging.debug('Task %s sends a push message: %s %s' % (
                    self.id, msg['plugin'], msg['message'],
                ))
            self.service.notify()

    def run(self):
        raise NotImplementedError()

    def push(self, plugin, message):
        self.pipe.put({
            'type': 'push',
            'plugin': plugin,
            'message': message,
        })


@service
class TasksService (object):
    def __init__(self, context):
        self.context = context
        self.tasks = {}
        self.notifications = BroadcastQueue()

    def start(self, task):
        self.tasks[task.id] = task
        task._start()
        self.send_update()

    def abort(self, id):
        self.tasks[task.id]._abort()

    def remove(self, id):
        self.tasks.pop(id)

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
