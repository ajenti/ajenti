from ajenti import apis
from ajenti.com import *
from ajenti.ui import *

class SquidRules(Plugin):
    implements(apis.squid.IPluginPart)
    
    weight = 20
    title = 'Rules'

    tab = 0
    cfg = 0
    parent = None
        
    def init(self, parent, cfg, tab):
        self.parent = parent
        self.cfg = cfg
        self.tab = tab
        parent._shuffling_rules = False
        parent._adding_rules = False

    def get_ui(self):
        t = UI.DataTable()
        t.appendChild(UI.DataTableRow(UI.Label(text='List'), UI.Label(text='Access'), UI.Label(text='ACL'), UI.Label(), header=True))
        for a in self.cfg.rules:
            t.appendChild(
                UI.DataTableRow(
                    UI.Label(text=a[0]), 
                    UI.Label(text=a[1]), 
                    UI.Label(text=a[2]), 
                    UI.DataTableCell(UI.MiniButton(text='Delete', id='del_rules/' + a[0] + '/' + a[1] + '/' + a[2]), hidden=True)
                )
              )
        vc = UI.VContainer(t, 
                UI.HContainer(
                    UI.Button(text='Add', id='add_rules'), 
                    UI.Button(text='Shuffle', id='shuffle_rules')
                )
             )    
        
        if self.parent._shuffling_rules:
            vc.vnode(self.get_ui_rules_shuffler())
        if self.parent._adding_rules:
            vc.vnode(self.get_ui_add())
           
        return vc
        
    def get_ui_add(self):
        li = UI.Select(name='list')
        for a in self.cfg.access_lists:
            li.appendChild(UI.SelectOption(text=a, value=a))
            
        c = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Access list:'),
                    li
                ),
                UI.LayoutTableRow(
                    UI.Radio(value='allow', text='Allow', name='type', checked=True),
                    UI.Radio(value='deny', text='Deny', name='type')
                ),
                UI.LayoutTableRow(
                    UI.Label(text='ACLs'),
                    UI.TextInput(name='acl')
                )
            )    
        return UI.DialogBox(c, title='Add access rule', id='dlgAddRules')
    
    def get_ui_rules_shuffler(self):
        li = UI.SortList(id='list')
        for p in self.cfg.rules:
            s = ' '.join(p)
            li.appendChild(UI.SortListItem(UI.Label(text=s), id=s))
            
        return UI.DialogBox(li, title='Shuffle HTTP access', id='dlgRules')
        
    def on_click(self, event, params, vars=None):
        if params[0] == 'shuffle_rules':
            self.parent._tab = self.tab
            self.parent._shuffling_rules = True
        if params[0] == 'add_rules':
            self.parent._tab = self.tab
            self.parent._adding_rules = True
        if params[0] == 'del_rules':
            self.parent._tab = self.tab
            self.cfg.rules.remove((params[1], params[2], params[3]))
            self.cfg.save()
            
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgRules':
            self.parent._tab = self.tab
            if vars.getvalue('action', '') == 'OK':
                l = vars.getvalue('list', '').split('|')
                self.cfg.rules = []
                for s in l:
                    t = s.split(' ')[0]
                    n = s.split(' ')[1]
                    v = ' '.join(s.split(' ')[2:])
                    self.cfg.rules.append((t, n, v))
                self.cfg.save()
            self.parent._shuffling_rules = False
        if params[0] == 'dlgAddRules':
            self.parent._tab = self.tab
            if vars.getvalue('action', '') == 'OK':
                l = vars.getvalue('list', '')
                t = vars.getvalue('type', '')
                a = vars.getvalue('acl', '')
                self.cfg.rules.append((l, t, a))
                self.cfg.save()
            self.parent._adding_rules = False

