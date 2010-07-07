from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

from backend import *


class ApachePlugin(CategoryPlugin):
    implements((ICategoryProvider, 50))

    text = 'Apache'
    icon = '/dl/apache/icon.png'
    platform = ['Debian', 'Ubuntu']
    
    def on_session_start(self):
        self._tab = 0
        self._editing_host = ''
        self._editing_module = ''
        
        
    def get_ui(self):
        status = 'is running' if is_running() else 'is stopped';
        panel = UI.PluginPanel(UI.Label(text=status), title='Apache web server', icon='/dl/apache/icon.png')

        if not is_installed():
            panel.appendChild(UI.VContainer(UI.ErrorBox(title='Error', text='Apache 2 is not installed')))
        else:
            panel.appendChild(self.get_default_ui())        

        return panel

    def get_default_ui(self):
        tc = UI.TabControl(active=self._tab)
        tc.add('Hosts', self.get_ui_hosts())
        tc.add('Modules', self.get_ui_mods())
        return tc
            
    def get_ui_hosts(self):
        th = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(), width='20px'),
                UI.DataTableCell(UI.Label(text='Name'), width='200px'),
                UI.DataTableCell(UI.Label(text=''), width='150px'),
                header=True
             )
        th.appendChild(hr)
        
        for h in list_hosts():
            if host_enabled(h):
                ctl = UI.MiniButton(text='Disable', id='stophost/' + h)
            else: 
                ctl = UI.MiniButton(text='Enable', id='starthost/' + h)
            r = UI.DataTableRow(
                    UI.Image(file=('/dl/core/ui/icon-' + ('enabled.png' if host_enabled(h) else 'disabled.png'))),
                    UI.Label(text=h),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(text='Edit', id='edithost/' + h),
                            ctl
                        ),
                        hidden=True
                    )
                )
            th.appendChild(r)
        
        p = UI.Container(th)
        if self._editing_host != '':
            dlg = UI.DialogBox(
                      UI.TextInputArea(name='config', text=read_host_config(self._editing_host).replace('\n', '[br]'), width=800, height=500),
                      title="Edit host config", id="dlgEditHost"
                  )
            p.appendChild(dlg)
        return p
        
    def get_ui_mods(self):
        tm = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(), width='20px'),
                UI.DataTableCell(UI.Label(text='Name'), width='200px'),
                UI.DataTableCell(UI.Label(text='')),
                header=True
             )
        tm.appendChild(hr)
        
        for h in list_modules():
            if module_enabled(h):
                ctl = UI.MiniButton(text='Disable', id='stopmod/' + h)
            else: 
                ctl = UI.MiniButton(text='Enable', id='startmod/' + h)
            if module_has_config(h):
                ctl = UI.Container(UI.MiniButton(text='Edit', id='editmod/' + h), ctl)
            r = UI.DataTableRow(
                    UI.Image(file=('/dl/core/ui/icon-' + ('enabled.png' if module_enabled(h) else 'disabled.png'))),
                    UI.Label(text=h),
                    UI.DataTableCell(
                        ctl, hidden=True
                    )
                )
            tm.appendChild(r)
        p = UI.Container(tm)
        if self._editing_module != '':
            dlg = UI.DialogBox(
                      UI.TextInputArea(name='config', text=read_module_config(self._editing_module).replace('\n', '[br]'), width=800, height=500),
                      title="Edit module config", id="dlgEditModule"
                  )
            p.appendChild(UI.vnode(dlg))
        return p            
    
    @event('minibutton/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'stophost':
            self._tab = 0
            disable_host(params[1])
        if params[0] == 'starthost':
            self._tab = 0
            enable_host(params[1])
        if params[0] == 'edithost':
            self._tab = 0
            self._editing_host = params[1]
        if params[0] == 'stopmod':
            self._tab = 1
            disable_module(params[1])
        if params[0] == 'startmod':
            self._tab = 1
            enable_module(params[1])
        if params[0] == 'editmod':
            self._tab = 1
            self._editing_module = params[1]

    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEditHost':
            if vars.getvalue('action', '') == 'OK':
                save_host_config(self._editing_host, vars.getvalue('config', ''))
            self._editing_host = '' 
        if params[0] == 'dlgEditModule':
            if vars.getvalue('action', '') == 'OK':
                save_module_config(self._editing_module, vars.getvalue('config', ''))
            self._editing_module = '' 
    
        
class ApacheContent(ModuleContent):
    module = 'apache'
    path = __file__
