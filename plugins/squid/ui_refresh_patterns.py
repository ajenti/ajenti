from ajenti import apis
from ajenti.com import *
from ajenti.ui import *


class SquidRefPats(Plugin):
    implements(apis.squid.IPluginPart)

    weight = 40
    title = 'Refresh patterns'

    tab = 0
    cfg = 0
    parent = None


    def init(self, parent, cfg, tab):
        self.parent = parent
        self.cfg = cfg
        self.tab = tab
        parent._adding_ref_pat = False
        parent._editing_ref_pat = -1

    def get_ui(self):
        t = UI.DataTable()
        t.appendChild(UI.DataTableRow(
                UI.Label(text='Regex'),
                UI.Label(text='Min'),
                UI.Label(text='%'),
                UI.Label(text='Max'),
                UI.Label(text='Options'),
                UI.Label(),
                header=True
              ))

        i = 0
        for a in self.cfg.ref_pats:
            t.appendChild(
                UI.DataTableRow(
                    UI.Label(text=a[0]),
                    UI.Label(text=a[1]),
                    UI.Label(text=a[2]),
                    UI.Label(text=a[3]),
                    UI.Label(text=a[4]),
                    UI.DataTableCell(
                        UI.HContainer(
                            UI.MiniButton(text='Edit', id='edit_ref_pat/' + str(i)),
                            UI.MiniButton(text='Delete', id='del_ref_pat/' + str(i))
                        ),
                        hidden=True
                   )
                )
              )
            i += 1

        vc = UI.VContainer(
                 t,
                 UI.Button(text='Add', id='add_ref_pat'),
             )

        if self.parent._adding_ref_pat:
            vc.vnode(self.get_ui_add())
        if self.parent._editing_ref_pat != -1:
            a = self.cfg.ref_pats[self.parent._editing_ref_pat]
            vc.vnode(self.get_ui_edit(a))

        return vc

    def get_ui_add(self):
        c = UI.HContainer(
                UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='Regex:'),
                        UI.TextInput(name='regex')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Min:'),
                        UI.TextInput(name='min')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Percents:'),
                        UI.TextInput(name='perc')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Max:'),
                        UI.TextInput(name='max')
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Options:'),
                        UI.TextInput(name='opts')
                    )
                )
            )
        return UI.DialogBox(c, title='Add refresh pattern', id='dlgAddRefPat')

    def get_ui_edit(self, a):
        c = UI.HContainer(
                UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='Regex:'),
                        UI.TextInput(name='regex', value=a[0])
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Min:'),
                        UI.TextInput(name='min', value=a[1])
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Percents:'),
                        UI.TextInput(name='perc', value=a[2])
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Max:'),
                        UI.TextInput(name='max', value=a[3])
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Options:'),
                        UI.TextInput(name='opts', value=a[4])
                    )
                )
            )
        return UI.DialogBox(c, title='Edit refresh pattern', id='dlgEditRefPat')

    def on_click(self, event, params, vars=None):
        if params[0] == 'add_ref_pat':
            self.parent._tab = self.tab
            self.parent._adding_ref_pat = True
        if params[0] == 'del_ref_pat':
            self.parent._tab = self.tab
            self.cfg.ref_pats.pop(int(params[1]))
        if params[0] == 'edit_ref_pat':
            self.parent._tab = self.tab
            self.parent._editing_ref_pat = int(params[1])

    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgAddRefPat':
            self.parent._tab = self.tab
            if vars.getvalue('action', '') == 'OK':
                r = vars.getvalue('regex', '')
                mn = vars.getvalue('min', '')
                p = vars.getvalue('perc', '')
                mx = vars.getvalue('max', '')
                o = vars.getvalue('opts', '')
                self.cfg.ref_pats.append((r, mn, p, mx, o))
                self.cfg.save()
            self.parent._adding_ref_pat = False
        if params[0] == 'dlgEditRefPat':
            self.parent._tab = self.tab
            if vars.getvalue('action', '') == 'OK':
                r = vars.getvalue('regex', '')
                mn = vars.getvalue('min', '')
                p = vars.getvalue('perc', '')
                mx = vars.getvalue('max', '')
                o = vars.getvalue('opts', '')
                self.cfg.ref_pats[self.parent._editing_ref_pat] = (r, mn, p, mx, o)
                self.cfg.save()
            self.parent._editing_ref_pat = -1
