import gevent

from ajenti.api import *
from ajenti.api.http import SocketPlugin
from ajenti.plugins.main.api import SectionPlugin, intent
from ajenti.ui import UIElement, p, on


@plugin
class Logs (SectionPlugin):
    def init(self):
        self.title = _('Logs')
        self.icon = 'list'
        self.category = _('System')

        self.append(self.ui.inflate('logs:main'))
        self.opendialog = self.find('opendialog')
        self.log = self.find('log')

    @on('open-button', 'click')
    def on_open(self):
        self.opendialog.visible = True

    @on('opendialog', 'button')
    def on_open_dialog(self, button):
        self.opendialog.visible = False

    @on('opendialog', 'select')
    def on_file_select(self, path=None):
        self.opendialog.visible = False
        self.select(path)

    @intent('view-log')
    def select(self, path):
        self.log.path = path
        self.activate()


@p('path', type=unicode)
@plugin
class LogView (UIElement):
    typeid = 'logs:log'


@plugin
class LogsSocket (SocketPlugin):
    name = '/log'

    def on_message(self, message):
        if message['type'] == 'select':
            self.path = message['path']
            self.reader = Reader(self.path)
            self.spawn(self.worker)
            self.emit('add', self.reader.data)

    def on_disconnect(self):
        self.reader.kill()

    def worker(self):
        while True:
            self.send_data(self.reader.read())

    def send_data(self, data):
        self.emit('add', data)


class Reader():
    def __init__(self, path):
        self.data = ''
        self.file = open(path, 'r')

    def read(self):
        l = self.file.readline()
        d = ''
        while not l:
            gevent.sleep(0.1)
            l = self.file.readline()
        while l:
            self.data += l
            d += l
            l = self.file.readline()
        return d

    def kill(self):
        self.file.close()
