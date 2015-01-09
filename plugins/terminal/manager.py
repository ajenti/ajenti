import logging
import uuid

from aj.api import *

from terminal import *


@service
class TerminalManager (object):
    def __init__(self, context):
        self.context = context
        self.terminals = {}

    def __getitem__(self, id):
        return self.terminals[id]

    def list(self):
        return [{
            'id': id,
            'command': self[id].command,
        } for id in self.terminals.keys()]

    def create(self):
        t = Terminal()
        id = str(uuid.uuid4())
        logging.info('Created terminal %s' % id)
        self.terminals[id] = t
        return id
    
    def kill(self, id):
        self.terminals.pop(id).kill()
