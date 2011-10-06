#coding: utf-8
from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import *
from ajenti import apis

import pwd
import psutil
import signal
import os


class TaskManagerPlugin(CategoryPlugin):
    text = 'Task manager'
    icon = '/dl/taskmgr/icon.png'
    folder = 'system'

    rev_sort = [
        'get_cpu_percent',
        'get_memory_percent',
    ]

    def on_session_start(self):
        self._sort = ('pid', False)
        self._info = None

    def sort_key(self, x):
        z = getattr(x,self._sort[0])
        return z() if callable(z) else z

    def get_ui(self):
        ui = self.app.inflate('taskmgr:main')
        l = psutil.get_process_list()
        l = sorted(l, key=self.sort_key)
        if self._sort[1]:
            l = reversed(l)

        for x in l:
            try:
                ui.append('list', UI.DTR(
                    UI.Image(file='/dl/core/ui/stock/service-%s.png'%('run' if x.is_running() else 'stop')),
                    UI.Label(text=str(x.pid)),
                    UI.Label(text=str(int(x.get_cpu_percent()))),
                    UI.Label(text=str(int(x.get_memory_percent()))),
                    UI.Label(text=pwd.getpwuid(x.uid)[0]),
                    UI.Label(text=x.name),
                    UI.TipIcon(
                        icon='/dl/core/ui/stock/info.png',
                        id='info/%i'%x.pid,
                        text='Info'
                    )
                ))
            except:
                pass

        hdr = ui.find('sort/'+self._sort[0])
        hdr.set('text', ('↑ ' if self._sort[1] else '↓ ')+ hdr['text'])

        if self._info is not None:
            try:
                p = filter(lambda x:x.pid==self._info, l)[0]
                iui = self.app.inflate('taskmgr:info')
                iui.find('name').set('text', '%i / %s'%(p.pid,p.name))
                iui.find('cmd').set('text', ' '.join("'%s'"%x for x in p.cmdline))
                iui.find('uid').set('text', '%s (%s)'%(pwd.getpwuid(p.uid)[0],p.uid))
                iui.find('gid').set('text', str(p.gid))
                iui.find('times').set('text', ' / '.join(str(x) for x in p.get_cpu_times()))
                if p.parent:
                    iui.find('parent').set('text', p.parent.name)
                    iui.find('parentinfo').set('id', 'info/%i'%p.parent.pid)
                else:
                    iui.remove('parentRow')

                sigs = [
                    (x, getattr(signal, x))
                    for x in dir(signal)
                    if x.startswith('SIG')
                ]

                for x in sigs:
                    iui.append('sigs', UI.SelectOption(
                        text=x[0], value=x[1]
                    ))
                ui.append('main', iui)
            except:
                pass

        return ui

    @event('button/click')
    def on_button(self, event, params, vars=None):
        if params[0] == 'info':
            self._info = int(params[1])
            return

        try:
            x = filter(lambda p:p.pid==self._info, psutil.get_process_list())[0]
        except:
            return
        if params[0] == 'suspend':
            x.suspend()
        if params[0] == 'resume':
            x.resume()

    @event('linklabel/click')
    def on_sort(self, event, params, vars=None):
        if params[1] == self._sort[0]:
            self._sort = (self._sort[0], not self._sort[1])
        else:
            self._sort = (params[1], params[1] in self.rev_sort)

    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgInfo':
            self._info = None
        if params[0] == 'frmKill':
            self._info = None
            try:
                x = filter(lambda p:p.pid==self._info, psutil.get_process_list())[0]
                x.kill(int(vars.getvalue('signal', None)))
                self.put_message('info', 'Killed process')
            except:
                self.put_message('err', 'Can\'t kill process')
