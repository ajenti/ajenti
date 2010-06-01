from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *

from api import *


class Services(CategoryPlugin):
    implements((ICategoryProvider, 50))

    text = 'Services'
    description = 'Control init.d scripts'
    icon = '/dl/services/icon.png'
    
    def on_init(self):
        self.svc_mgr = self.app.grab_plugins(IServiceManager)[0]


    def on_session_start(self):
        self._labeltext = ''

    def get_ui(self):
        h = UI.HContainer(
               UI.Image(file='/dl/services/bigicon.png'),
               UI.Spacer(width=10),
               UI.VContainer(
                    UI.Label(text='Service manager', size=5),
               )
            )

        ts = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(), width='20px'),
                UI.DataTableCell(UI.Label(text='Name'), width='200px'),
                UI.DataTableCell(UI.Label(text='Controls'), width='150px'),
                header=True
             )
        ts.appendChild(hr)

        lst = self.svc_mgr.list_all()
        for svc in lst:
            if svc.status == 'running':
                ctl = UI.HContainer(
                          UI.LinkLabel(text='Stop', id='stop/' + svc.name),
                          UI.LinkLabel(text='Restart', id='restart/' + svc.name)
                      )
            else:
                ctl = UI.LinkLabel(text='Start', id='start/' + svc.name)
            fn = '/dl/services/' + ('run.png' if svc.status == 'running' else 'stop.png')
            row = UI.DataTableRow(
                    UI.Image(file=fn),
                    UI.Label(text=svc.name),
                    ctl
                  )
            ts.appendChild(row)
              

        p = UI.VContainer(
                h,
                UI.Spacer(height=20),
                UI.VContainer(
                    ts
                )
            )

        return p

    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'start':
            self.svc_mgr.start(params[1])
        if params[0] == 'restart':
            self.svc_mgr.restart(params[1])
        if params[0] == 'stop':
            self.svc_mgr.stop(params[1])


class ServicesContent(ModuleContent):
    module = 'services'
    path = __file__
