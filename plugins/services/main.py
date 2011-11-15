from ajenti.com import implements
from ajenti.api import *
from ajenti.ui import *
from ajenti import apis

from groups import *


class ServicesPlugin(CategoryPlugin):
    text = 'Services'
    icon = '/dl/services/icon.png'
    folder = 'system'

    def on_init(self):
        self.svc_mgr = self.app.get_backend(apis.services.IServiceManager)
        self.groupmgr = ServiceGroups(self.app)
        
    def on_session_start(self):
        self._editing = None

    def get_ui(self):
        ui = self.app.inflate('services:main')
        ts = ui.find('list')

        lst = sorted(self.svc_mgr.list_all(), key=lambda x: x.status)
        for svc in lst:
            row = self.get_row(svc)
            ts.append(row)

        for g in sorted(self.groupmgr.groups.keys()):
            gui = self.app.inflate('services:group')
            gui.find('edit').set('id', 'edit/'+g)
            gui.find('delete').set('id', 'delete/'+g)
            gui.find('name').set('text', g)
            for s in self.groupmgr.groups[g]:
                try:
                    svc = filter(lambda x:x.name==s, lst)[0]
                    gui.append('list', self.get_row(svc))
                except:
                    pass
            ui.append('groups', gui)

        if self._editing is not None:
            has = self._editing in self.groupmgr.groups.keys()
            eui = self.app.inflate('services:edit')
            eui.find('name').set('value', self._editing)
            for svc in self.svc_mgr.list_all():
                eui.append('services', UI.Checkbox(
                    name=svc.name,
                    text=svc.name,
                    checked=has and (svc.name in self.groupmgr.groups[self._editing]),
                ))
            ui.append('main', eui)

        return ui

    def get_row(self, svc):
        if svc.status == 'running':
            ctl = UI.HContainer(
                      UI.TipIcon(text='Stop', icon='/dl/core/ui/stock/service-stop.png', id='stop/' + svc.name),
                      UI.TipIcon(text='Restart', icon='/dl/core/ui/stock/service-restart.png', id='restart/' + svc.name)
                  )
        else:
            ctl = UI.TipIcon(text='Start', icon='/dl/core/ui/stock/service-run.png', id='start/' + svc.name)
        fn = '/dl/core/ui/stock/service-' + ('run.png' if svc.status == 'running' else 'stop.png')
        row = UI.DTR(
                UI.Image(file=fn),
                UI.Label(text=svc.name),
                ctl
              )
        return row
                      
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'start':
            self.svc_mgr.start(params[1])
        if params[0] == 'restart':
            self.svc_mgr.restart(params[1])
        if params[0] == 'stop':
            self.svc_mgr.stop(params[1])
        if params[0] == 'addGroup':
            self._editing = ''
        if params[0] == 'delete':
            del self.groupmgr.groups[params[1]]
            self.groupmgr.save()
        if params[0] == 'edit':
            self._editing = params[1]

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit':
            if vars.getvalue('action') == 'OK':
                svcs = []
                for svc in self.svc_mgr.list_all():
                    if vars.getvalue(svc.name) == '1':
                        svcs.append(svc.name)
                if self._editing != '':
                    del self.groupmgr.groups[self._editing]                        
                self.groupmgr.groups[vars.getvalue('name')] = sorted(svcs)
                self.groupmgr.save()
            self._editing = None

