from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from api import *

class PackageManager(CategoryPlugin):
    implements((ICategoryProvider, 60))

    text = 'Packages'
    description = 'Install software'
    icon = '/dl/pkgman/icon.png'


    def on_init(self):
        self.mgr = self.app.grab_plugins(IPackageManager)[0]

    def on_session_start(self):
        self._labeltext = ''
        self._status = Status()
        self._tab = 0
        self._confirm_apply = False
        self._in_progress = False
        self._search = {}
        self.mgr = self.app.grab_plugins(IPackageManager)[0]
        self.mgr.refresh(self._status)

    def get_ui(self):
        if self._in_progress and not self.mgr.is_busy():
            self.mgr.refresh(self._status)
            self._status.pending = {}
        self._in_progress = self.mgr.is_busy()


        h = UI.HContainer(
               UI.Image(file='/dl/pkgman/bigicon.png'),
               UI.Spacer(width=10),
               UI.VContainer(
                   UI.Label(text='Package manager', size=5),
                   UI.Spacer(height=10),
                   UI.HContainer(
                       UI.Button(text='Refresh', id='refresh'),
                       UI.Button(text='Get lists', id='getlists'),
                   )
               )
            )


        tabs = UI.TabControl(active=self._tab)

        # Upgrades
        tu = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Package'), width="200px"),
                UI.DataTableCell(UI.Label(text='New version'), width="100px"),
                UI.DataTableCell(UI.Label(text=''), width="80px"),
                header=True
             )
        tu.appendChild(hr)

        for p in self._status.upgradeable:
            p = self._status.upgradeable[p]
            r = UI.DataTableRow(
                    UI.Label(text=p.name, bold=(self._status.pending.has_key(p.name))),
                    UI.Label(text=p.version),
                    UI.LinkLabel(text="Select", id="upgrade/"+p.name)
                )
            tu.appendChild(r)

        cu = UI.VContainer(tu)
        tabs.add('Upgrades', cu)


        # Search
        ts = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Package'), width="150px"),
                UI.DataTableCell(UI.Label(text='Description'), width="350px"),
                UI.DataTableCell(UI.Label(text=''), width="100px"),
                header=True
             )
        ts.appendChild(hr)

        for p in self._search:
            r = UI.DataTableRow(
                    UI.Label(text=p, bold=(self._status.pending.has_key(p))),
                    UI.Label(text=self._search[p].description),
                    UI.LinkLabel(text='Install', id='install/'+p) if self._search[p].state == 'removed' else
                    UI.LinkLabel(text='Remove', id='remove/'+p)
                )
            ts.appendChild(r)

        cs = UI.VContainer(
                UI.HContainer(
                    UI.Form(
                        UI.HContainer(
                            UI.TextInput(name='query'),
                            UI.Button(text='Search', onclick='form', form='frmSearch')
                        ),
                        id='frmSearch',
                        action='/handle/dialog/submit/frmSearch'
                    )
                ),
                UI.Spacer(height=20),
                ts
             )

        tabs.add('Search', cs)


        # Pending
        tu = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Package'), width="200px"),
                UI.DataTableCell(UI.Label(text=''), width="80px"),
                header=True
             )
        tu.appendChild(hr)

        for p in self._status.pending:
            if self._status.pending[p] == 'install':
                r = UI.DataTableRow(
                        UI.Label(text=p),
                        UI.LinkLabel(text="Cancel", id="cancel/"+p)
                    )
                tu.appendChild(r)


        ti = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Package'), width="200px"),
                UI.DataTableCell(UI.Label(text=''), width="80px"),
                header=True
             )
        ti.appendChild(hr)

        for p in self._status.pending:
            if self._status.pending[p] == 'remove':
                r = UI.DataTableRow(
                        UI.Label(text=p),
                        UI.LinkLabel(text="Cancel", id="cancel/"+p)
                    )
                ti.appendChild(r)

        cp = UI.VContainer(
                UI.Label(text='Upgrade / install:', size=3),
                tu,
                UI.Spacer(height=20),
                UI.Label(text='Remove:', size=3),
                ti,
                UI.Spacer(height=20),
                UI.Button(text='Apply now', id='apply')
             )

        tabs.add('Pending actions', cp)


        # Apply?
        res = UI.DataTable()
        if self._confirm_apply:
            r = self.mgr.get_expected_result(self._status)
            for x in r:
                t = UI.DataTableRow(
                        UI.Label(text=('Install/upgrade' if r[x] == 'install' else 'Remove')),
                        UI.Label(text=x, bold=True)
                    )
                res.appendChild(t)

        dlg = UI.DialogBox(
                res,
                UI.Spacer(height=20),
                title="Apply changes?", id="dlgApply", action="/handle/dialog/submit/dlgApply"
              )

        # Progress
        pb = UI.ProgressBox(
                title = "Appplying changes",
                status = self.mgr.get_busy_status()
             )

        p = UI.VContainer(
                h,
                UI.Spacer(height=20),
                tabs,
                dlg if self._confirm_apply else None,
                pb if self._in_progress else None
            )

        return p

    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'refresh':
            self.mgr.refresh(self._status)
        if params[0] == 'getlists':
            self.mgr.get_lists()
        if params[0] == 'apply':
            self._tab = 2
            self._confirm_apply = True

    @event('linklabel/click')
    def on_llclick(self, event, params, vars=None):
        if params[0] == 'install':
            self._tab = 1
            self.mgr.mark_install(self._status, params[1])
        if params[0] == 'upgrade':
            self._tab = 0
            self.mgr.mark_install(self._status, params[1])
        if params[0] == 'cancel':
            self._tab = 2
            self.mgr.mark_cancel(self._status, params[1])

    @event('dialog/submit')
    def on_dialog(self, event, params, vars=None):
        if params[0] == 'dlgApply':
            self._confirm_apply = False
            if vars.getvalue('action', '') == 'OK':
                self.mgr.apply(self._status)
                self._in_progress = True
        if params[0] == 'frmSearch':
            self._tab = 1
            if vars.getvalue('query','') != '':
                self._search = self.mgr.search(vars.getvalue('query',''))


class PackageManagerContent(ModuleContent):
    module = 'pkgman'
    path = __file__
    
