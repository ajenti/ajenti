from ajenti.com import *
from ajenti.apis import API
from ajenti.app.helpers import CategoryPlugin, event
from ajenti.ui import UI
from ajenti import apis


class Webserver(API):
    
    class VirtualHost:
        names = None
        enabled = False
        
        def __init__(self):
            self.enabled = False
            self.names = []
            
                    
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
                            
            return UI.VContainer(tbl, UI.Button(text='Add host', id='addhost'))
        
        @event('minibutton/click')
        def on_click(self, event, params, vars=None):
            if params[0] == 'togglehost':
                h = self._backend.get_hosts()[params[1]]
                if h.enabled:
                    self._backend.disable_host(params[1])
                else:
                    self._backend.enable_host(params[1])
          
