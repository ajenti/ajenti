import gevent
import time

from ajenti.api import *
from ajenti.api.http import SocketPlugin
from ajenti.plugins.configurator.api import ClassConfigEditor
from ajenti.plugins.main.api import SectionPlugin, intent
from ajenti.ui import UIElement, p, on


@plugin
class LogsConfigEditor (ClassConfigEditor):
    title = _('Logs')
    icon = 'list'

    def init(self):
        self.append(self.ui.inflate('logs:config'))


@plugin
class Logs (SectionPlugin):
    default_classconfig = {'root': '/var/log'}
    classconfig_editor = LogsConfigEditor

    def init(self):
        self.title = _('Logs')
        self.icon = 'list'
        self.category = _('System')

        self.append(self.ui.inflate('logs:main'))
        self.opendialog = self.find('opendialog')
        self.log = self.find('log')

    def on_page_load(self):
        self.opendialog.root = self.classconfig['root']
        self.opendialog.navigate(self.opendialog.root)

    @on('open-button', 'click')
    def on_open(self):
        self.opendialog.show()

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

    def init(self):
        self.reader = None

    def on_message(self, message):
        if message['type'] == 'select':
            self.path = message['path']
            self.reader = Reader(self.path)
            self.spawn(self.worker)
            self.emit('add', self.reader.data)

    def on_disconnect(self):
        if self.reader:
            self.reader.kill()

    def worker(self):
        while True:
            data = self.reader.read()
            if data is not None:
                self.send_data(data)

    def send_data(self, data):
        self.emit('add', data)


class Reader():
    def __init__(self, path):
        self.data = ''
        self.file = open(path, 'r')

    def read(self):
        ctr = 0
        try:
            l = self.file.readline()
        except:
            return None
        d = ''
        while not l:
            gevent.sleep(0.33)
            l = self.file.readline()
        while l:
            gevent.sleep(0)
            d += l
            ctr += 1
            l = self.file.readline()
            if len(d) > 1024 * 128:
                break
        return d

    def kill(self):
        self.file.close()
