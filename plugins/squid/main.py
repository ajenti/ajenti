from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import CategoryPlugin, ModuleContent, EventProcessor, event

from backend import *


class SquidContent(ModuleContent):
    module = 'squid'
    path = __file__


class SquidPlugin(CategoryPlugin):
    implements((ICategoryProvider, 70))

    text = 'Squid'
    icon = '/dl/squid/icon.png'
    platform = ['Debian', 'Ubuntu']

    def on_init(self):
        self.cfg = SquidConfig()
        self.cfg.load()
        self.cfg.save()
        
    def on_session_start(self):
        self._tab = 0
        self._shuffling_acls = False
        
    def get_ui(self):
        status = 'is running' if is_running() else 'is stopped';
        panel = UI.PluginPanel(UI.Label(text=status), title='Squid Proxy Server', icon='/dl/squid/icon.png')

        if not is_installed():
            panel.appendChild(UI.VContainer(UI.ErrorBox(title='Error', text='Squid is not installed')))
        else:
            panel.appendChild(self.get_default_ui())        

        return panel


    def get_default_ui(self):
        tc = UI.TabControl(active=self._tab)
        tc.add('ACLs', self.get_ui_acls())
 #       tc.add('Modules', self.get_ui_mods())
        return tc

    def get_ui_acls(self):
        t = UI.DataTable()
        t.appendChild(UI.DataTableRow(UI.Label(text='Type'), UI.Label(text='Parameters'), UI.Label(), header=True))
        for a in self.cfg.acls:
            t.appendChild(
                UI.DataTableRow(
                    UI.Label(text=a[0]), 
                    UI.Label(text=a[1]), 
                    UI.Label()
                )
              )
        frm = UI.FormBox(t, miscbtnid='shuffle_acls', miscbtn='Shuffle', id='frmACLs')
        vc = UI.VContainer(frm)
        
        if self._shuffling_acls:
            vc.vnode(self.get_ui_acls_shuffler())
            
        return vc
        
    def get_ui_acls_shuffler(self):
        li = UI.SortList(id='list')

        for p in self.cfg.acls:
            s = ' '.join(p)
            li.appendChild(UI.SortListItem(UI.Label(text=s), id=s))
        
        return UI.DialogBox(li, title='Shuffle ACLs', id='dlgACLs')
        
    
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'shuffle_acls':
            self._tab = 0
            self._shuffling_acls = True
            
    @event('dialog/submit')
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgACLs':
            self._tab = 0
            if vars.getvalue('action', '') == 'OK':
#                self.config.set('users', vars.getvalue('login', ''), self.hashpw(vars.getvalue('password', '')))
                self.cfg.save()
            self._shuffling_acls = False
 
