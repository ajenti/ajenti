from aj.util import LazyModule

import logging
uuid = LazyModule('uuid') # uses ctypes, forks, screws up Upstart

from aj.api import *

from terminal import *


@service
class TerminalManager (object):
    def __init__(self, context):
        self.context = context
        self.terminals = {}

    def __getitem__(self, id):
        return self.terminals[id]

    def __contains__(self, id):
        return id in self.terminals

    def list(self):
        return [{
            'id': id,
            'command': self[id].command,
        } for id in self.terminals.keys()]

    def create(self, **kwargs):
        id = str(uuid.uuid4())
        t = Terminal(self, id, **kwargs)
        logging.info('Created terminal %s' % id)
        self.terminals[id] = t
        return id

    def kill(self, id):
        self.terminals[id].kill()
        self.remove(id)

    def remove(self, id):
        self.terminals.pop(id)
