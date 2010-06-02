from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

from backend import *


class Apache(CategoryPlugin):
    implements((ICategoryProvider, 50))

    text = 'Apache'
    description = 'Web server'
    icon = '/dl/apache/icon.png'
    platform = ['Debian', 'Ubuntu']
    
    def on_session_start(self):
        self._tab = 0
        self._editing_host = ''
        self._editing_module = ''
        
        
    def get_ui(self):
        hdr = UI.HContainer(
               UI.Image(file='/dl/apache/bigicon.png'),
               UI.Spacer(width=10),
               UI.VContainer(
                   UI.Label(text='Apache web server', size=5),
                   UI.Label(text=('is running' if is_running() else 'is stopped'))
               )
            )
            
        
        th = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(), width='20px'),
                UI.DataTableCell(UI.Label(text='Name'), width='200px'),
                UI.DataTableCell(UI.Label(text='Controls'), width='150px'),
                header=True
             )
        th.appendChild(hr)
        
        for h in list_hosts():
            if host_enabled(h):
                ctl = UI.LinkLabel(text='Disable', id='stophost/' + h)
            else: 
                ctl = UI.LinkLabel(text='Enable', id='starthost/' + h)
            r = UI.DataTableRow(
                    UI.Image(file=('/dl/apache/' + ('run.png' if host_enabled(h) else 'stop.png'))),
                    UI.Label(text=h),
                    UI.HContainer(
                        UI.LinkLabel(text='Edit', id='edithost/' + h),
                        ctl
                    )
                )
            th.appendChild(r)
            
        phosts = UI.VContainer(th)
        
        tm = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(), width='20px'),
                UI.DataTableCell(UI.Label(text='Name'), width='200px'),
                UI.DataTableCell(UI.Label(text='Controls'), width='150px'),
                header=True
             )
        tm.appendChild(hr)
        
        for h in list_modules():
            if module_enabled(h):
                ctl = UI.LinkLabel(text='Disable', id='stopmod/' + h)
            else: 
                ctl = UI.LinkLabel(text='Enable', id='startmod/' + h)
            r = UI.DataTableRow(
                    UI.Image(file=('/dl/apache/' + ('run.png' if module_enabled(h) else 'stop.png'))),
                    UI.Label(text=h),
                    UI.HContainer(
                        (UI.LinkLabel(text='Edit', id='editmod/' + h) if module_has_config(h) else None),
                        ctl
                    )
                )
            tm.appendChild(r)
        
        pmods = UI.VContainer(tm)
        
        tc = UI.TabControl(active=self._tab)
        tc.add('Hosts', phosts)
        tc.add('Modules', pmods)

        p = UI.VContainer(
                hdr,
                UI.Spacer(height=20),
                tc
            )

        if self._editing_host != '':
            dlg = UI.DialogBox(
                      UI.TextInputArea(name='config', text=read_host_config(self._editing_host).replace('\n', '[br]'), width=800, height=500),
                      title="Edit host config", id="dlgEditHost", action="/handle/dialog/submit/dlgEditHost"
                  )
            p.appendChild(UI.vnode(dlg))

        if self._editing_module != '':
            dlg = UI.DialogBox(
                      UI.TextInputArea(name='config', text=read_module_config(self._editing_module).replace('\n', '[br]'), width=800, height=500),
                      title="Edit module config", id="dlgEditModule", action="/handle/dialog/submit/dlgEditModule"
                  )
            p.appendChild(UI.vnode(dlg))

        return p

    @event('linklabel/click')
    def on_llclick(self, event, params, vars=None):
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
