from ajenti.com import implements
from ajenti.api import *
from ajenti.ui import *
from ajenti import apis


class ServicesPlugin(CategoryPlugin):
    text = 'Services'
    icon = '/dl/services/icon_small.png'
    folder = 'system'

    def on_init(self):
        self.svc_mgr = self.app.get_backend(apis.services.IServiceManager)
        
    def on_session_start(self):
        self._labeltext = ''

    def get_ui(self):
        ts = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(), width='20px'),
                UI.DataTableCell(UI.Label(text='Name'), width='200px'),
                UI.DataTableCell(UI.Label(text='')),
                header=True
             )
        ts.append(hr)

        lst = sorted(self.svc_mgr.list_all(), key=lambda x: x.status)
        running = 0
        for svc in lst:
            if svc.status == 'running':
                running += 1
                ctl = UI.HContainer(
                          UI.MiniButton(text='Stop', id='stop/' + svc.name),
                          UI.MiniButton(text='Restart', id='restart/' + svc.name)
                      )
            else:
                ctl = UI.MiniButton(text='Start', id='start/' + svc.name)
            fn = '/dl/core/ui/stock/status-' + ('running.png' if svc.status == 'running' else 'stopped.png')
            row = UI.DataTableRow(
                    UI.Image(file=fn),
                    UI.Label(text=svc.name),
                    UI.DataTableCell(
                        ctl, hidden=True
                    )
                  )
            ts.append(row)

        panel = UI.PluginPanel(
            UI.Label(text='%i out of %i running'%(running,len(lst))), 
            title='Service Manager', 
            icon='/dl/services/icon.png'
        )

        panel.append(ts)
        return panel

    @event('minibutton/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'start':
            self.svc_mgr.start(params[1])
        if params[0] == 'restart':
            self.svc_mgr.restart(params[1])
        if params[0] == 'stop':
            self.svc_mgr.stop(params[1])


class ServicesContent(ModuleContent):
    module = 'services'
    widget_files = ['widgets.xslt']
    css_files = ['services.css']
    path = __file__
