from ajenti.com import *
from ajenti.apis import API
from ajenti.app.helpers import CategoryPlugin, event
from ajenti.ui import UI
from ajenti import apis


class Webserver(API):
    
    class VirtualHost:
        names = None
        enabled = False
        servername = None
        params = None
        locations = None
        
        def __init__(self):
            self.enabled = False
            self.names = []
            self.servername = ''
            self.params = []
            self.locations = []
            
            
    class Location:
        pass
                        
    class WebserverPlugin(apis.services.ServiceControlPlugin):
        abstract = True
        
        ws_service = 'none'
        ws_title = 'none'
        ws_icon = 'none'
        ws_name = 'none'
        ws_backend = None

        def on_init(self):
            self.service_name = self.ws_service

        def on_session_start(self):
            self._backend = self.ws_backend
            self._editing_host = None
            
        def get_main_ui(self):
            panel = UI.ServicePluginPanel(title=self.ws_title, icon=self.ws_icon, status=self.service_status, servicename=self.service_name)

            if not self._backend.is_installed():
                panel.append(UI.VContainer(UI.ErrorBox(title='Error', text='%s is not installed'%self.ws_name)))
            else:
                panel.append(self.get_default_ui())

            return panel

        def get_default_ui(self):
            tc = UI.TabControl(active=self._tab)
            tc.add('Hosts', self.get_ui_hosts())
            return tc
            
        def get_ui_hosts(self):
            tbl = UI.DataTable(
                    UI.DataTableRow(
                        UI.Label(),
                        UI.Label(text='Name'),
                        UI.Label(),
                        header=True
                    )
                  )
               
            hosts = self._backend.get_hosts()
            for x in sorted(hosts.keys()):
                tbl.append(UI.DataTableRow(
                            UI.Image(file='/dl/core/ui/stock/status-%sabled.png'%(
                                'en' if hosts[x].enabled else 'dis')),
                            UI.Label(text=x),
                            UI.DataTableCell(
                                UI.HContainer(
                                    UI.MiniButton(
                                        id='edithost/'+x, 
                                        text='Edit'
                                    ),
                                    UI.MiniButton(
                                        id='togglehost/'+x, 
                                        text='Disable' if hosts[x].enabled else 'Enable'
                                    ),
                                    spacing=0
                                ),
                                hidden=True
                            )
                          ))
                            
            ui = UI.VContainer(tbl, UI.Button(text='Add host', id='addhost'))
            
            if self._editing_host is not None:
                ui.append(
                    self.get_ui_edit_host(
                        self._backend.get_hosts()[self._editing_host]
                    )
                )
            return ui
                
        def get_ui_edit_host(self, h):
            dlg = UI.DialogBox(
                    UI.LayoutTable(
                        UI.LayoutTableRow(
                            UI.Label(text='Listen at:'),
                            UI.TextInputArea(
                                text='\n'.join(h.names),
                                name='listenat',
                                help='One per line',
                                height=50
                            )
                        ),
                        UI.LayoutTableRow(
                            UI.Label(text='Server name:'),
                            UI.TextInput(value=h.servername, name='servername')
                        )
                    ),
                    id='dlgEditHost'
                  )
            return dlg
            
        @event('minibutton/click')
        def on_click(self, event, params, vars=None):
            if params[0] == 'togglehost':
                h = self._backend.get_hosts()[params[1]]
                if h.enabled:
                    self._backend.disable_host(params[1])
                else:
                    self._backend.enable_host(params[1])
            if params[0] == 'edithost':
                self._editing_host = params[1]

        @event('dialog/submit')
        def on_submit(self, event, params, vars):
            if params[0] == 'dlgEditHost':
                self._editing_host = None
                
                
