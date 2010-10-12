import time

from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.plugins.core.api import *
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
        self._info = None
        
    def get_ui(self):
        ctl = UI.HContainer(
                UI.Button(text='Refresh', id='refresh'),
                UI.Button(text='Get lists', id='getlists'),
                UI.Button(text='Apply now', id='apply')
              )
        panel = UI.PluginPanel(ctl, title='Package Manager', icon='/dl/pkgman/icon.png')
        pnl = UI.Container()
        panel.append(pnl)
        pnl.append(self.get_default_ui())

        if self._confirm_apply:
            res = UI.DataTable(UI.DataTableRow(
                    UI.DataTableCell(width=20),
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

        if self._info is not None:
            pnl.append(self.get_ui_info())
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
                UI.DataTableCell(
                    width=20
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
                            UI.HContainer(
                                UI.MiniButton(text='Info', id='info/'+p.name),
                                UI.MiniButton(text='Select', id='upgrade/'+p.name),
                                spacing=0
                            ),
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
                            UI.MiniButton(text='Info', id='info/'+p),
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
                            UI.MiniButton(text='Info', id='info/'+p),
                            UI.MiniButton(text='Cancel', id='cancel/'+p),
                            hidden=True
                        )
                    )
                tbl_pkgs.append(r)
                
            ui_misc = \
                UI.VContainer(
                    UI.Button(text='Cancel all', id='cancelall'),
                )        
                
        list_cats = UI.List(
            UI.ListItem(UI.Label(text='Upgradeable'), id='upgrades', active=self._current=='upgrades'),
            UI.ListItem(UI.Label(text='Search'), id='search', active=self._current=='search'),
            UI.ListItem(UI.Label(text='Pending'), id='pending', active=self._current=='pending'),
            width=100,
            height=300
        )
        
        ui = UI.LayoutTable(
            UI.LayoutTableRow(
                list_cats,
                UI.ScrollContainer(
                    tbl_pkgs,
                    height=300,
                    width=500
                ),
                ui_misc
            ),
            height=300,
            width=700
        )
        
        return ui

    def get_ui_info(self):
        pkg = self._info
        info = self.mgr.get_info(pkg)
        iui = self.mgr.get_info_ui(pkg)
        ui = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.LayoutTableCell(
                        UI.Image(file='/dl/pkgman/icon.png'),
                        rowspan=6
                    ),
                    UI.Label(text='Package:', bold=True),
                    UI.Label(text=pkg, bold=True)
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Installed:'),
                    UI.Label(text=info.installed)
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Available:'),
                    UI.Label(text=info.available)
                ),
                UI.LayoutTableRow(
                    UI.Label(text='Desription:'),
                    UI.Container(
                        UI.Label(text=info.description),
                        width=300
                    )
                ),
                UI.LayoutTableRow(
                    UI.LayoutTableCell(
                        UI.HContainer(
                            UI.MiniButton(text='(Re)install', id='install/'+pkg),
                            UI.MiniButton(text='Remove', id='remove/'+pkg)
                        ),
                        colspan=2
                    )
                ),
                UI.LayoutTableRow(
                    UI.LayoutTableCell(
                        iui,
                        colspan=2
                    )
                )
            )
        return UI.DialogBox(ui, id='dlgInfo')
            
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
            time.sleep(0.5)
        if params[0] == 'apply':
            self._confirm_apply = True
            time.sleep(0.5)
        if params[0] == 'install':
            self.mgr.mark_install(self._status, params[1])
            self._info = None
        if params[0] == 'remove':
            self.mgr.mark_remove(self._status, params[1])
            self._info = None
        if params[0] == 'upgrade':
            self.mgr.mark_install(self._status, params[1])
        if params[0] == 'cancel':
            self.mgr.mark_cancel(self._status, params[1])
        if params[0] == 'upgradeall':
            for p in self._status.upgradeable:
                self.mgr.mark_install(self._status, p)
        if params[0] == 'info':
            self._info = params[1]
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
            q = vars.getvalue('query','')
            if q != '':
                self._search = self.mgr.search(q, self._status)
        if params[0] == 'dlgInfo':
            self._info = None
            
        
class PackageManagerProgress(Plugin):
    implements(IProgressBoxProvider)
    title = 'Packages'
    icon = '/dl/pkgman/icon_small.png'
    can_abort = True
    
    def __init__(self):
        self.mgr = self.app.get_backend(apis.pkgman.IPackageManager)

    def has_progress(self):         
        return self.mgr.is_busy()
        
    def get_progress(self):
        return self.mgr.get_busy_status()
    
    def abort(self):
        self.mgr.abort()
        
                
class PackageManagerContent(ModuleContent):
    module = 'pkgman'
    path = __file__        
