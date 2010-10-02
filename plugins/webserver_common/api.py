from ajenti.com import *
from ajenti.apis import API
from ajenti.app.helpers import CategoryPlugin, event
from ajenti.ui import UI
from ajenti import apis


class Webserver(API):
    
    class VirtualHost:
        def __init__(self):
            self.name = ''
            self.config = ''            


    class Module:
        def __init__(self):
            self.name = ''
            self.config = ''          
            self.has_config = False
              
                                
    class WebserverPlugin(apis.services.ServiceControlPlugin):
        abstract = True
        
        ws_service = 'none'
        ws_title = 'none'
        ws_icon = 'none'
        ws_name = 'none'
        ws_backend = None
        ws_mods = False
        ws_vhosts = True
        
        def on_init(self):
            self.service_name = self.ws_service
            self.tab_hosts = 0
            self.tab_mods = 1 if self.ws_vhosts else 0
            
        def on_session_start(self):
            self._tab = 0
            self._backend = self.ws_backend
            self._creating_host = False
            self._editing_host = None
            self._editin_mod = None
            
        def get_main_ui(self):
            panel = UI.ServicePluginPanel(title=self.ws_title, icon=self.ws_icon, status=self.service_status, servicename=self.service_name)

            if not self._backend.is_installed():
                panel.append(UI.VContainer(UI.ErrorBox(title='Error', text='%s is not installed'%self.ws_name)))
            else:
                panel.append(self.get_default_ui())

            return panel

        def get_default_ui(self):
            tc = UI.TabControl(active=self._tab)
            if self.ws_vhosts:
                tc.add('Hosts', self.get_ui_hosts())
            if self.ws_mods:
                tc.add('Modules', self.get_ui_mods())
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
                                    UI.WarningMiniButton(
                                        id='deletehost/'+x, 
                                        text='Delete',
                                        msg='Delete host %s'%x
                                    ),
                                    spacing=0
                                ),
                                hidden=True
                            )
                          ))
                            
            ui = UI.VContainer(tbl, UI.Button(text='Add host', id='addhost'))
            
            if self._creating_host:
                ui.append(
                    UI.InputBox(
                        text='Host config name:', 
                        id='dlgCreateHost'
                    )
                )

            if self._editing_host is not None:
                ui.append(
                    UI.AreaInputBox(
                        text='Host config:', 
                        value=self._backend.get_hosts()[self._editing_host].config,
                        id='dlgEditHost'
                    )
                )
                
            return ui
            
        def get_ui_mods(self):
            tbl = UI.DataTable(UI.DataTableRow(
                    UI.DataTableCell(UI.Label(), width='20px'),
                    UI.DataTableCell(UI.Label(text='Name'), width='200px'),
                    UI.DataTableCell(UI.Label(text='')),
                    header=True
                 ))
            
            mods = self._backend.get_mods()
            for x in sorted(mods.keys()):
                tbl.append(UI.DataTableRow(
                            UI.Image(file='/dl/core/ui/stock/status-%sabled.png'%(
                                'en' if mods[x].enabled else 'dis')),
                            UI.Label(text=x),
                            UI.DataTableCell(
                                UI.HContainer(
                                    UI.MiniButton(
                                        id='editmod/'+x, 
                                        text='Edit'
                                    ) if mods[x].has_config else None,
                                    UI.MiniButton(
                                        id='togglemod/'+x, 
                                        text='Disable' if mods[x].enabled else 'Enable'
                                    ),
                                    spacing=0
                                ),
                                hidden=True
                            )
                          ))
            
            ui = UI.Container(tbl)
            if self._editing_mod is not None:
                ui.append(
                    UI.AreaInputBox(
                        text='Module config:', 
                        value=self._backend.get_mods()[self._editing_mod].config,
                        id='dlgEditMod'
                    )
                )
                
            return ui
                
        @event('button/click')
        @event('minibutton/click')
        def on_click(self, event, params, vars=None):
            if params[0] == 'togglehost':
                self._tab = self.tab_hosts
                h = self._backend.get_hosts()[params[1]]
                if h.enabled:
                    self._backend.disable_host(params[1])
                else:
                    self._backend.enable_host(params[1])
            if params[0] == 'deletehost':
                self._tab = self.tab_hosts
                self._backend.delete_host(params[1])
            if params[0] == 'edithost':
                self._tab = self.tab_hosts
                self._editing_host = params[1]
            if params[0] == 'addhost':
                self._tab = self.tab_hosts
                self._creating_host = True
                
            if params[0] == 'togglemod':
                self._tab = self.tab_mods
                h = self._backend.get_mods()[params[1]]
                if h.enabled:
                    self._backend.disable_mod(params[1])
                else:
                    self._backend.enable_mod(params[1])
            if params[0] == 'editmod':
                self._tab = self.tab_mods
                self._editing_mod = params[1]

        @event('dialog/submit')
        def on_submit(self, event, params, vars):
            if params[0] == 'dlgCreateHost':
                if vars.getvalue('action', '') == 'OK':
                    h = apis.webserver.VirtualHost()
                    h.config = self._backend.host_template 
                    h.name = vars.getvalue('value', '')
                    self._backend.save_host(h)
                self._creating_host = False
            if params[0] == 'dlgEditHost':
                if vars.getvalue('action', '') == 'OK':
                    h = self._backend.get_hosts()[self._editing_host]
                    h.config = vars.getvalue('value', '')
                    self._backend.save_host(h)
                self._editing_host = None
            if params[0] == 'dlgEditMod':
                if vars.getvalue('action', '') == 'OK':
                    h = self._backend.get_mods()[self._editing_mod]
                    h.config = vars.getvalue('value', '')
                    self._backend.save_mod(h)
                self._editing_mod = None

                
