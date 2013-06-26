import psutil
import os

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder

from ajenti.profiler import *


@plugin
class TaskManager (SectionPlugin):
    def init(self):
        self.title = _('Processes')
        self.icon = 'th-list'
        self.category = _('System')
        self.append(self.ui.inflate('taskmgr:main'))

        def post_item_bind(object, collection, item, ui):
            ui.find('term').on('click', self.on_term, item)
            ui.find('kill').on('click', self.on_kill, item)

        self.find('processes').post_item_bind = post_item_bind

        self.binder = Binder(None, self)

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        profile('Process list')

        self.processes = list(psutil.process_iter())
        for p in self.processes:
            p._name = p.name
            p._cmd = ' '.join(p.cmdline)
            p._cpu = p.get_cpu_percent(interval=0)
            p._ram = '%i K' % int(p.get_memory_info()[0] / 1024)
            p._ppid = p.ppid
            try:
                p._username = p.username
            except:
                p._username = '?'

        self.binder.reset(self).autodiscover().populate()
        profile_end('Process list')

    def on_term(self, p):
        os.kill(p.pid, 15)
        self.refresh()

    def on_kill(self, p):
        os.kill(p.pid, 9)
        self.refresh()
