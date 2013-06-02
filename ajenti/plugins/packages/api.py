import subprocess

from ajenti.api import *


class PackageInfo (object):
    def __init__(self):
        self.name = ''
        self.state = 'r'
        self.action = None
        self.version = ''
        self.description = ''

    @property
    def _icon(self):
        if self.action == 'i':
            return 'ok-circle'
        if self.action == 'r':
            return 'remove-circle'
        return 'ok' if self.state == 'i' else None


@interface
class PackageManager (BasePlugin):
    def init(self):
        self.upgradeable = []

    def get_lists(self):
        pass

    def refresh(self):
        pass

    def search(self, query):
        return []

    def do(self, actions, callback=lambda: 0):
        pass
