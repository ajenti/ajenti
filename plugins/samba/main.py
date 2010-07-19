from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

import backend


class SambaPlugin(CategoryPlugin):
    implements((ICategoryProvider, 50))

    text = 'Samba'
    icon = '/dl/samba/icon.png'

    def on_session_start(self):
        self._tab = 0
        self._cfg = backend.SambaConfig()
        self._cfg.load()
        self._editing_share = None
        
    def get_ui(self):
        panel = UI.PluginPanel(UI.Button(text='Apply config', id='restart'), title='Samba', icon='/dl/samba/icon.png')

        panel.appendChild(self.get_default_ui())        

        return panel

    def get_default_ui(self):
        tc = UI.TabControl(active=self._tab)
        tc.add('Shares', self.get_ui_shares())
        return tc
            
    def get_ui_shares(self):
        th = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Name'), width='200px'),
                UI.DataTableCell(UI.Label(text='Path'), width='200px'),
                UI.DataTableCell(UI.Label()),
                header=True
             )
        th.appendChild(hr)
        
        for h in self._cfg.get_shares():
            r = UI.DataTableRow(
                    UI.Label(text=h),
                    UI.Label(text=self._cfg.shares[h]['path']),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(text='Edit', id='editshare/' + h),
                            UI.WarningMiniButton(text='Delete', id='delshare/' + h)
                        ),
                        hidden=True
                    )
                )
            th.appendChild(r)
        
        th = UI.VContainer(th, UI.Button(text='Add new share', id='newshare'))
        
        if not self._editing_share is None:
            if self._editing_share == '':
                th.vnode(self.get_ui_edit_share())
            else:
                th.vnode(self.get_ui_edit_share(
                            self._cfg.shares[self._editing_share]
                        ))
        return th
        
    def get_ui_edit_share(self, s=None):
        if s is None or s == '':
            s = self._cfg.new_share()
            
        dlg = UI.DialogBox(
                  UI.LayoutTable(
                      UI.LayoutTableRow(
                          UI.Label(text='Name:'),
                          UI.TextInput(name='name', value='new')
                      ) if self._editing_share == '' else None,
                      UI.LayoutTableRow(
                          UI.Label(text='Path:'),
                          UI.TextInput(name='path', value=s['path'])
                      ),
                      UI.LayoutTableRow(
                          UI.Label(text='Valid users:'),
                          UI.TextInput(name='valid users', value=s['valid users'])
                      ),
                      UI.LayoutTableRow(
                          UI.LayoutTableCell(
                              UI.Checkbox(text='Available', name='available', checked=s['available']=='yes'),
                              colspan=2
                          )
                      ),
                      UI.LayoutTableRow(
                          UI.LayoutTableCell(
                              UI.Checkbox(text='Browseable', name='browseable', checked=s['browseable']=='yes'),
                              colspan=2
                          )
                      ),
                      UI.LayoutTableRow(
                          UI.LayoutTableCell(
                              UI.Checkbox(text='Read only', name='read only', checked=s['read only']=='yes'),
                              colspan=2
                          )
                      ),
                      UI.LayoutTableRow(
                          UI.LayoutTableCell(
                              UI.Checkbox(text='Guest access', name='guest ok', checked=s['guest ok']=='yes'),
                              colspan=2
                          )
                      ),
                      UI.LayoutTableRow(
                          UI.LayoutTableCell(
                              UI.Checkbox(text='Force guest', name='guest only', checked=s['guest only']=='yes'),
                              colspan=2
                          )
                      )
                  ),
                  id='dlgEditShare',
                  title='Edit share'  
              )
        return dlg
    
    @event('minibutton/click')
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'restart':
            backend.restart()
        if params[0] == 'editshare':
            self._editing_share = params[1]
        if params[0] == 'delshare':
            self._cfg.shares.pop(params[1])
            self._cfg.save()
        if params[0] == 'newshare':
            self._editing_share = ''
       
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEditShare':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                es = self._editing_share
                if es == '': 
                    es = vars.getvalue('name', 'new')
                    self._cfg.shares[es] = self._cfg.new_share()
                    
                self._cfg.set_param_from_vars(es, 'path', vars)
                self._cfg.set_param_from_vars(es, 'valid users', vars)
                self._cfg.set_param_from_vars_yn(es, 'available', vars)
                self._cfg.set_param_from_vars_yn(es, 'browseable', vars)
                self._cfg.set_param_from_vars_yn(es, 'read only', vars)
                self._cfg.set_param_from_vars_yn(es, 'guest ok', vars)
                self._cfg.set_param_from_vars_yn(es, 'guest only', vars)
                self._cfg.save()
            self._editing_share = None
        
class SambaContent(ModuleContent):
    module = 'samba'
    path = __file__
    
