import psutil
import os

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder

from ajenti.profiler import *

def get(value):
    '''
    psutil 2 compatibility layer
    '''
    return value() if callable(value) else value

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
        self.sorting = '_cpu'
        self.sorting_reverse = True

        for x in ['_cpu', 'pid', '_sort_ram', '_sort_name']:
            self.find('sort-by-' + x).on('click', self.sort, x)

    def on_page_load(self):
        self.refresh()

    def sort(self, by):
        if self.sorting == by:
            self.sorting_reverse = not self.sorting_reverse
        else:
            self.sorting_reverse = by in ['_cpu', '_ram']
        self.sorting = by
        self.refresh()

    def refresh(self):
        self.processes = list(psutil.process_iter())
        for p in self.processes:
            try:
                p._name = get(p.name)
                p._cmd = ' '.join(get(p.cmdline))
                p._cpu = p.get_cpu_percent(interval=0)
                p._ram = '%i K' % int(p.get_memory_info()[0] / 1024)
                p._ppid = get(p.ppid)
                p._sort_ram = p.get_memory_info()[0]
                p._sort_name = get(p.name).lower()
                try:
                    p._username = get(p.username)
                except:
                    p._username = '?'
            except psutil.NoSuchProcess:
                self.processes.remove(p)

        self.processes = sorted(self.processes, key=lambda x: getattr(x, self.sorting, None), reverse=self.sorting_reverse)
        self.binder.setup(self).populate()

    def on_term(self, p):
        os.kill(p.pid, 15)
        self.refresh()

    def on_kill(self, p):
        os.kill(p.pid, 9)
        self.refresh()
