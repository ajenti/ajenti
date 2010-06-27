from ajenti import apis
from ajenti.com import *
from ajenti.ui import *

class SquidHTTPAccess(Plugin):
    implements(apis.squid.IPluginPart)
    
    weight = 20
    title = 'HTTP Access'

    tab = 0
    cfg = 0
    parent = None
        
    def init(self, parent, cfg, tab):
        self.parent = parent
        self.cfg = cfg
        self.tab = tab
        parent._shuffling_http_access = False

    def get_ui(self):
        t = UI.DataTable()
        t.appendChild(UI.DataTableRow(UI.Label(text='Access'), UI.Label(text='ACL'), UI.Label(), header=True))
        for a in self.cfg.http_access:
            t.appendChild(
                UI.DataTableRow(
                    UI.Label(text=a[0]), 
                    UI.Label(text=a[1]), 
                    UI.Label()
                )
              )
        frm = UI.FormBox(t, miscbtnid='shuffle_http_access', miscbtn='Shuffle', id='frmHttpAccess')
        vc = UI.VContainer(frm)
        
        if self.parent._shuffling_http_access:
            vc.vnode(self.get_ui_http_access_shuffler())
           
        return vc
        
    def get_ui_http_access_shuffler(self):
        li = UI.SortList(id='list')
        for p in self.cfg.http_access:
            s = ' '.join(p)
            li.appendChild(UI.SortListItem(UI.Label(text=s), id=s))
            
        return UI.DialogBox(li, title='Shuffle HTTP access', id='dlgHttpAccess')
        
    def on_click(self, event, params, vars=None):
        if params[0] == 'shuffle_http_acces':
            self.parent._tab = self.tab
            self.parent._shuffling_http_access = True

    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgHttpAccess':
            self.parent._tab = self.tab
            if vars.getvalue('action', '') == 'OK':
                l = vars.getvalue('list', '').split('|')
                self.cfg.http_access = []
                for s in l:
                    n = s.split(' ')[0]
                    v = ' '.join(s.split(' ')[1:])
                    self.cfg.http_access.append((n, v))
                self.cfg.save()
            self.parent._shuffling_http_access = False

