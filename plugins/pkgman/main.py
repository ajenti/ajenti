from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti import apis


class PackageManagerPlugin(CategoryPlugin):
    text = 'Packages'
    icon = '/dl/pkgman/icon_small.png'
    folder = 'system'

    def on_init(self):
        self.mgr = self.app.get_backend(apis.pkgman.IPackageManager)
        if self._need_refresh:
            self_need_refresh = False
            self.mgr.refresh(self._status)
        if self._in_progress and not self.mgr.is_busy():
            self.mgr.refresh(self._status)
            self._status.pending = {}
        self._in_progress = self.mgr.is_busy()
    
    def on_session_start(self):
        self._status = apis.pkgman.Status()
        self._current = 'upgrades'
        self._need_refresh = True
        self._confirm_apply = False
        self._in_progress = False
        self._search = {}
        self._search_query = ''
            
    def get_ui(self):
        ctl = UI.HContainer(
                UI.Button(text='Refresh', id='refresh'),
                UI.Button(text='Get lists', id='getlists'),
              )
        panel = UI.PluginPanel(ctl, title='Package Manager', icon='/dl/pkgman/icon.png')
        pnl = UI.Container()
        panel.append(pnl)
        pnl.append(self.get_default_ui())

        if self._confirm_apply:
            res = UI.DataTable(UI.DataTableRow(
                    UI.Label(),
                    UI.Label(text='Package'),
                    header=True
                  ), width='100%', noborder=True)
                  
            if self._confirm_apply:
                r = self.mgr.get_expected_result(self._status)
                for x in r:
                    i = '/dl/pkgman/package-'
                    i += 'upgrade' if r[x] == 'install' else 'remove'
                    t = UI.DataTableRow(
                            UI.Image(file=i+'.png'),
                            UI.Label(text=x)
                        )
                    res.append(t)

            dlg = UI.DialogBox(
                    UI.ScrollContainer(res, width=300, height=300),
                    id='dlgApply'
                  )
            pnl.append(dlg)


        if self._in_progress:
            pb = UI.ProgressBox(
                    title = 'Appplying changes',
                    status = self.mgr.get_busy_status()
                 )
            pnl.append(pb)

        return panel

    def _get_icon(self, p):
        r = '/dl/pkgman/package-'
        if p in self._status.pending.keys():
            if self._status.pending[p] == 'install':
                r += 'upgrade'
            else:
                r += 'remove'
        else:
            if p in self._status.full.keys():
                r += 'installed'
                if p in self._status.upgradeable.keys():
                    r += '-outdated'
            else:
                r += 'available'
        r += '.png'
        return r
            
    def get_default_ui(self):
        tbl_pkgs = UI.DataTable(
            UI.DataTableRow(
                UI.LayoutTableCell(
                    widht=20
                ),
                UI.Label(text='Name'),
                UI.Label(text='Version'),
                UI.Label(text='Description'),
                UI.Label(),
                header=True
            ),
            width='100%',
            noborder=True
        )
        
        if self._current == 'upgrades':
            for p in sorted(self._status.upgradeable.keys()):
                p = self._status.upgradeable[p]
                r = UI.DataTableRow(
                        UI.Image(file=self._get_icon(p.name)),
                        UI.Label(text=p.name),
                        UI.Label(text=p.version),
                        UI.Label(text=p.description),
                        UI.DataTableCell(
                            UI.MiniButton(text='Select', id='upgrade/'+p.name),
                            hidden=True
                        )
                    )
                tbl_pkgs.append(r)
                
            ui_misc = UI.Button(text='Select all', id='upgradeall')

        if self._current == 'search':
            for p in self._search:
                r = UI.DataTableRow(
                        UI.Image(file=self._get_icon(p)),
                        UI.Label(text=p),
                        UI.Label(text=self._search[p].version),
                        UI.Label(text=self._search[p].description),
                        UI.DataTableCell(
                            UI.MiniButton(text='Install', id='install/'+p) if self._search[p].state == 'removed' else
                            UI.MiniButton(text='Remove', id='remove/'+p),
                            hidden=True
                    )
                )
                tbl_pkgs.append(r)
            
            ui_misc = UI.FormBox(
                        UI.VContainer(
                            UI.TextInput(name='query', size=10, value=self._search_query),
                            UI.Button(text='Search', onclick='form', form='frmSearch')
                        ),
                        id='frmSearch',
                        hideok=True,
                        hidecancel=True
                    )
        
        if self._current == 'pending':
            for p in sorted(self._status.pending.keys()):
                r = UI.DataTableRow(
                        UI.Image(file=self._get_icon(p)),
                        UI.Label(text=p),
                        UI.Label(),
                        UI.Label(),
                        UI.DataTableCell(
                            UI.MiniButton(text='Cancel', id='cancel/'+p),
                            hidden=True
                        )
                    )
                tbl_pkgs.append(r)
                
            ui_misc = \
                UI.VContainer(
                    UI.Button(text='Cancel all', id='cancelall'),
                    UI.Button(text='Apply now', id='apply')
                )        
                
        list_cats = UI.List(
            UI.ListItem(UI.Label(text='Upgradeable'), id='upgrades', active=self._current=='upgrades'),
            UI.ListItem(UI.Label(text='Search'), id='search', active=self._current=='search'),
            UI.ListItem(UI.Label(text='Pending'), id='pending', active=self._current=='pending'),
            width=100,
            height=100
        )
        
        ui = UI.LayoutTable(
            UI.LayoutTableRow(
                list_cats,
                UI.LayoutTableCell(
                    UI.ScrollContainer(
                        tbl_pkgs,
                        height=300,
                        width=600
                    ),
                    rowspan=2
                )
            ),
            UI.LayoutTableRow(
                UI.LayoutTableCell(
                    ui_misc,
                    height=100
                )
            ),
            height=300,
            width=700
        )
        
        return ui

    @event('listitem/click')
    def on_li_click(self, event, params, vars=None):
        self._current = params[0]

    @event('button/click')
    @event('minibutton/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'refresh':
            self.mgr.refresh(self._status)
        if params[0] == 'getlists':
            self.mgr.get_lists()
        if params[0] == 'apply':
            self._confirm_apply = True
        if params[0] == 'install':
            self.mgr.mark_install(self._status, params[1])
        if params[0] == 'remove':
            self.mgr.mark_remove(self._status, params[1])
        if params[0] == 'upgrade':
            self.mgr.mark_install(self._status, params[1])
        if params[0] == 'cancel':
            self.mgr.mark_cancel(self._status, params[1])
        if params[0] == 'upgradeall':
            for p in self._status.upgradeable:
                self.mgr.mark_install(self._status, p)
        if params[0] == 'cancelall':
            self._status.upgradeable = {}
        
    @event('dialog/submit')
    @event('form/submit')
    def on_dialog(self, event, params, vars=None):
        if params[0] == 'dlgApply':
            self._confirm_apply = False
            if vars.getvalue('action', '') == 'OK':
                self.mgr.apply(self._status)
                self._in_progress = True
                self._status.pending = {}
        if params[0] == 'frmSearch':
            self._tab = 1
            q = vars.getvalue('query','')
            if q != '':
                self._search = self.mgr.search(q, self._status)
        
"""
class PackageManagerPlugin(CategoryPlugin):
    text = 'Packages'
    icon = '/dl/pkgman/icon_small.png'
    folder = 'system'

    def on_init(self):
        self.mgr = self.app.get_backend(apis.pkgman.IPackageManager)

    def on_session_start(self):
        self._labeltext = ''
        self._status = apis.pkgman.Status()
        self._tab = 0
        self._confirm_apply = False
        self._in_progress = False
        self._search = {}
        self._need_refresh = True

    def get_ui(self):
        if self._need_refresh:
            self._need_refresh = False
            self.mgr.refresh(self._status)

        if self._in_progress and not self.mgr.is_busy():
            self.mgr.refresh(self._status)
            self._status.pending = {}
        self._in_progress = self.mgr.is_busy()

        ctl = UI.HContainer(
                UI.Button(text='Refresh', id='refresh'),
                UI.Button(text='Get lists', id='getlists'),
              )
        panel = UI.PluginPanel(ctl, title='Package Manager', icon='/dl/pkgman/icon.png')
        panel.append(self.get_default_ui())

        return panel

    def get_default_ui(self):
        tabs = UI.TabControl(active=self._tab)
        tabs.add('Upgrades', self.get_ui_upgrades())
        tabs.add('Search', self.get_ui_search())
        tabs.add('Pending actions', self.get_ui_pending())

        pnl = UI.VContainer(tabs)

        if self._confirm_apply:
            res = UI.DataTable(UI.DataTableRow(
                    UI.Label(text='Action'),
                    UI.Label(text='Package'),
                    header=True
                  ))
                  
            if self._confirm_apply:
                r = self.mgr.get_expected_result(self._status)
                for x in r:
                    t = UI.DataTableRow(
                            UI.Label(text=('Install/upgrade' if r[x] == 'install' else 'Remove')),
                            UI.Label(text=x, bold=True)
                        )
                    res.append(t)

            dlg = UI.DialogBox(
                    res,
                    title="Apply changes?", id="dlgApply"
                  )
            pnl.append(dlg)


        if self._in_progress:
            pb = UI.ProgressBox(
                    title = "Appplying changes",
                    status = self.mgr.get_busy_status()
                 )
            pnl.append(pb)

        return pnl

    def get_ui_upgrades(self):
        tu = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Package'), width="350px"),
                UI.DataTableCell(UI.Label(text='New version'), width="100px"),
                UI.DataTableCell(UI.Label(text='')),
                header=True
             )
        tu.append(hr)

        for p in sorted(self._status.upgradeable.keys()):
            p = self._status.upgradeable[p]
            r = UI.DataTableRow(
                    UI.Label(text=p.name, bold=(self._status.pending.has_key(p.name))),
                    UI.Label(text=p.version),
                    UI.DataTableCell(
                        UI.MiniButton(text="Select", id="upgrade/"+p.name),
                        hidden=True
                    )
                )
            tu.append(r)

        return tu

    def get_ui_search(self):
        ts = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Package'), width="150px"),
                UI.DataTableCell(UI.Label(text='Description'), width="350px"),
                UI.DataTableCell(UI.Label(text='')),
                header=True
             )
        ts.append(hr)

        for p in self._search:
            r = UI.DataTableRow(
                    UI.Label(text=p, bold=(self._search[p].state == 'installed')),
                    UI.Label(text=self._search[p].description),
                    UI.DataTableCell(
                        UI.MiniButton(text='Install', id='install/'+p) if self._search[p].state == 'removed' else
                        UI.MiniButton(text='Remove', id='remove/'+p),
                        hidden=True
                    )
                )
            ts.append(r)

        cs = UI.VContainer(
                UI.HContainer(
                    UI.FormBox(
                        UI.HContainer(
                            UI.TextInput(name='query'),
                            UI.Button(text='Search', onclick='form', form='frmSearch')
                        ),
                        id='frmSearch',
                        hideok=True,
                        hidecancel=True
                    )
                ),
                UI.Spacer(height=20),
                ts
             )
        return cs

    def get_ui_pending(self):
        tu = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Package'), width="200px"),
                UI.DataTableCell(UI.Label(text='')),
                header=True
             )
        tu.append(hr)

        for p in sorted(self._status.pending.keys()):
            if self._status.pending[p] == 'install':
                r = UI.DataTableRow(
                        UI.Label(text=p),
                        UI.DataTableCell(
                            UI.MiniButton(text="Cancel", id="cancel/"+p),
                            hidden=True
                        )
                    )
                tu.append(r)


        ti = UI.DataTable()
        hr = UI.DataTableRow(
                UI.DataTableCell(UI.Label(text='Package'), width="200px"),
                UI.DataTableCell(UI.Label(text='')),
                header=True
             )
        ti.append(hr)

        for p in sorted(self._status.pending.keys()):
            if self._status.pending[p] == 'remove':
                r = UI.DataTableRow(
                        UI.Label(text=p),
                        UI.DataTableCell(
                            UI.MiniButton(text="Cancel", id="cancel/"+p),
                            hidden=True
                        )
                    )
                ti.append(r)

        cp = UI.VContainer(
                UI.Label(text='Upgrade / install:', size=3),
                tu,
                UI.Label(text='Remove:', size=3),
                ti,
                UI.Button(text='Apply now', id='apply')
             )

        return cp

    @event('button/click')
    @event('minibutton/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'refresh':
            self.mgr.refresh(self._status)
        if params[0] == 'getlists':
            self.mgr.get_lists()
        if params[0] == 'apply':
            self._tab = 2
            self._confirm_apply = True
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
    @event('form/submit')
    def on_dialog(self, event, params, vars=None):
        if params[0] == 'dlgApply':
            self._confirm_apply = False
            if vars.getvalue('action', '') == 'OK':
                self.mgr.apply(self._status)
                self._in_progress = True
                self._status.pending = {}
        if params[0] == 'frmSearch':
            self._tab = 1
            if vars.getvalue('query','') != '':
                self._search = self.mgr.search(vars.getvalue('query',''))

"""

class PackageManagerContent(ModuleContent):
    module = 'pkgman'
    path = __file__
    
