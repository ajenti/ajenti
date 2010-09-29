from ajenti.com import *
from ajenti.apis import API
from ajenti.app.helpers import CategoryPlugin, event
from ajenti.ui import UI
from ajenti import apis


class Webserver(API):
    
    class VirtualHost:
        def __init__(self):
            self.name = ''
            self.enabled = False
            self.names = []
            self.servername = ''
            self.params = []
            self.locations = []
            self.ssl = False
            self.ssl_cert = ''
            self.ssl_key = ''

            
    class Location:
        def __init__(self):
            self.params = ''
            self.name = ''
            
                        
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
            self._tab = 0
            self._backend = self.ws_backend
            self._editing_host = None
            self._editing_location = None
            self._host_tab = 0
            
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
            if self._editing_location is not None:
                ui.append(
                    UI.AreaInputBox(
                        text='Location config:', 
                        value=self._backend.get_hosts()[self._editing_host].\
                            locations[self._editing_location].params,
                        id='dlgEditLocation'
                    )
                )
                
            return ui
                
        def get_ui_edit_host(self, h):
            locations = UI.DataTable(
                    UI.DataTableRow(
                        UI.Label(text='Name'),
                        UI.Label(),
                        header=True
                    )
                )
                
            params = '\n'.join('%s %s;'%x for x in h.params)
            
            idx = 0
            for l in h.locations:
                n = l.name
                locations.append(UI.DataTableRow(
                        UI.Label(text=n),
                        UI.DataTableCell(
                            UI.HContainer(
                                UI.MiniButton(id='editlocation/%i'%idx, text='Edit'),
                                UI.WarningMiniButton(
                                    id='deletelocation/%i'%idx, 
                                    text='Delete',
                                    msg='Delete location %s'%n
                                ),
                                spacing=0
                            ),
                            hidden=True
                        )
                   ))   
                idx += 1
            
            tc = UI.TabControl(active=self._host_tab)
            tc.add('General',
                    UI.LayoutTable(
                        UI.LayoutTableRow(
                            UI.Label(text='Listen at:'),
                            UI.TextInputArea(
                                value='\n'.join(h.names),
                                name='listenat',
                                help='One per line',
                                height=50,
                                width=300
                            )
                        ),
                        UI.LayoutTableRow(
                            UI.Label(text='Server name:'),
                            UI.TextInput(value=h.servername, name='servername')
                        ),
                        UI.LayoutTableRow(
                            UI.Label(text='Misc parameters:'),
                            UI.TextInputArea(
                                value=params,
                                name='params',
                                height=100,
                                width=300
                            )
                        )
                    ))
                    
            tc.add('Locations', UI.VContainer(
                        locations,
                        UI.Button(text='Add location', id='addlocation')
                   ))
                   
            tc.add('SSL', UI.LayoutTable(
                        UI.LayoutTableRow(
                            UI.LayoutTableCell(
                                UI.Checkbox(text='SSL', checked=h.ssl, name='ssl'),
                                colspan=2
                            )
                        ),
                        UI.LayoutTableRow(
                            UI.Label(text='SSL certificate:'),
                            UI.TextInput(value=h.ssl_cert, name='ssl_cert')
                        ),
                        UI.LayoutTableRow(
                            UI.Label(text='SSL key file:'),
                            UI.TextInput(value=h.ssl_key, name='ssl_key')
                        )
                    ))
                    
            return UI.DialogBox(tc, id='dlgEditHost')
            
        @event('minibutton/click')
        def on_click(self, event, params, vars=None):
            if params[0] == 'togglehost':
                self._tab = 0
                h = self._backend.get_hosts()[params[1]]
                if h.enabled:
                    self._backend.disable_host(params[1])
                else:
                    self._backend.enable_host(params[1])
            if params[0] == 'edithost':
                self._tab = 0
                self._editing_host = params[1]

            if params[0] == 'editlocation':
                self._host_tab = 1
                self._editing_location = int(params[1])

        @event('dialog/submit')
        def on_submit(self, event, params, vars):
            if params[0] == 'dlgEditHost':
                if vars.getvalue('action', '') == 'OK':
                    h = self._backend.get_hosts()[self._editing_host]
                    h.names = vars.getvalue('listenat', '').split('\n')
                    self._backend.save_host(h)
                self._editing_host = None
            if params[0] == 'dlgEditLocation':
                if vars.getvalue('action', '') == 'OK':
                    h = self._backend.get_hosts()[self._editing_host]
                    l = h.locations[self._editing_location]
                    l.params = vars.getvalue('value', '')
                    self._backend.save_host(h)
                self._editing_location = None
                
                
