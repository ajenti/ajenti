import logging
import subprocess

from aj.plugins.core.api.tasks import Task
from aj.auth import authorize


class Transfer(Task):
    name = _('File transfer')

    def __init__(self, context, destination=None, items=None):
        Task.__init__(self, context)
        self.destination = destination
        self.items = items

    @authorize('filesystem:write')
    def run(self):
        logging.info('Transferring %s items into %s', len(self.items), self.destination)
        self.destination = self.destination.rstrip('/')

        for idx, item in enumerate(self.items):
            self.report_progress(message=item['item']['name'], done=idx, total=len(self.items))
            if item['mode'] == 'move':
                logging.info('Moving %s', item['item']['path'])
                r = subprocess.call([
                    'mv', item['item']['path'], self.destination
                ])
                if r != 0:
                    logging.warn('mv exited with code %i', r)
            if item['mode'] == 'copy':
                logging.info('Copying %s', item['item']['path'])
                r = subprocess.call([
                    'cp', '-a', item['item']['path'], self.destination
                ])
                if r != 0:
                    logging.warn('cp exited with code %i', r)

        self.push('filesystem', 'refresh')


class Delete(Task):
    name = _('Deleting')

    def __init__(self, context, items=None):
        Task.__init__(self, context)
        self.items = items

    @authorize('filesystem:write')
    def run(self):
        logging.info('Deleting %s items', len(self.items))

        for idx, item in enumerate(self.items):
            self.report_progress(message=item['name'], done=idx, total=len(self.items))
            logging.info('Deleting %s', item['path'])
            r = subprocess.call([
                'rm', '-r', '-f', item['path'],
            ])
            if r != 0:
                logging.warn('rm exited with code %i', r)

        self.push('filesystem', 'refresh')
