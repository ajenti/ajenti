import time

from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.plugins.core.api import *
from ajenti import apis


class PackageManagerPlugin(CategoryPlugin):
    text = 'Packages'
    icon = '/dl/pkgman/icon.png'
    folder = 'system'

    def on_init(self):
        self.mgr = ComponentManager.get().find('pkgman')

        if self._in_progress and not self.mgr.is_busy():
            self._need_refresh = True
            self.mgr.mark_cancel_all(self._status)
            self._in_progress = False

        if self._need_refresh:
            self.mgr.refresh()
            self._need_refresh = False

        self._status = self.mgr.get_status()

    def on_session_start(self):
        self._status = None
        self._current = 'upgrades'
        self._need_refresh = False
        self._confirm_apply = False
        self._in_progress = False
        self._search = {}
        self._search_query = ''
        self._info = None

    def get_counter(self):
        c = len(ComponentManager.get().find('pkgman').get_status().upgradeable)
        if c > 0:
            return str(c)

    def _get_icon(self, p):
        r = '/dl/pkgman/package-'
        if p in self._status.pending.keys():
            if self._status.pending[p] == 'install':
                r += 'upgrade'
            else:
                r += 'remove'
        else:
            if p in self._status.full.keys():
                if self._status.full[p].state == 'broken':
                    r += 'broken'
                elif p in self._status.upgradeable.keys():
                    r += 'outdated'
                else:
                    r += 'installed'
            else:
                r += 'available'
        r += '.png'
        return r

    def get_ui(self):
        ui = self.app.inflate('pkgman:main')

        ui.find('tabs').set('active', self._current)

        pnl = ui.find('main')

        if self._confirm_apply:
            res = UI.DT(UI.DTR(
                    UI.DTH(width=20),
                    UI.DTH(UI.Label(text='Package')),
                    header=True
                  ), width='100%', noborder=True)

            if self._confirm_apply:
                r = self.mgr.get_expected_result(self._status)
                for x in r:
                    i = '/dl/pkgman/package-'
                    i += 'upgrade' if r[x] == 'install' else 'remove'
                    t = UI.DTR(
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

        tbl_pkgs = ui.find('list')

        if self._current == 'upgrades':
            for p in sorted(self._status.upgradeable.keys()):
                p = self._status.upgradeable[p]
                r = UI.DTR(
                        UI.Image(file=self._get_icon(p.name)),
                        UI.Label(text=p.name),
                        UI.Label(text=p.version),
                        UI.Label(text=p.description),
                            UI.HContainer(
                                UI.TipIcon(icon='/dl/core/ui/stock/info.png', text='Info', id='info/'+p.name),
                                UI.TipIcon(icon='/dl/pkgman/package-available.png', text='Deselect', id='cancel/'+p.name)
                                    if p.name in self._status.pending else
                                UI.TipIcon(icon='/dl/pkgman/package-upgrade.png', text='Select', id='upgrade/'+p.name),
                                spacing=0
                            ),
                    )
                tbl_pkgs.append(r)

        if self._current == 'broken':
            for p in sorted(self._status.full.keys()):
                p = self._status.full[p]
                if p.state != 'broken': continue
                r = UI.DTR(
                        UI.Image(file=self._get_icon(p.name)),
                        UI.Label(text=p.name),
                        UI.Label(text=p.version),
                        UI.Label(text=p.description),
                            UI.HContainer(
                                UI.TipIcon(icon='/dl/core/ui/stock/info.png', text='Info', id='info/'+p.name),
                                UI.TipIcon(icon='/dl/pkgman/package-install.png', text='Reinstall', id='install/'+p.name),
                                UI.TipIcon(icon='/dl/pkgman/package-remove.png', text='Remove', id='remove/'+p.name),
                                spacing=0
                            ),
                    )
                tbl_pkgs.append(r)

        if self._current == 'search':
            for p in self._search:
                r = UI.DTR(
                        UI.Image(file=self._get_icon(p)),
                        UI.Label(text=p),
                        UI.Label(text=self._search[p].version),
                        UI.Label(text=self._search[p].description),
                            UI.HContainer(
                                UI.TipIcon(icon='/dl/core/ui/stock/info.png', text='Info', id='info/'+p),
                                UI.TipIcon(icon='/dl/pkgman/package-install.png', text='Install', id='install/'+p) if self._search[p].state == 'removed' else
                                UI.TipIcon(icon='/dl/pkgman/package-remove.png', text='Remove', id='remove/'+p),
                                spacing=0
                            ),
                )
                tbl_pkgs.append(r)

        if self._current == 'pending':
            for p in sorted(self._status.pending.keys()):
                r = UI.DTR(
                        UI.Image(file=self._get_icon(p)),
                        UI.Label(text=p),
                        UI.Label(),
                        UI.Label(),
                            UI.HContainer(
                                UI.TipIcon(icon='/dl/core/ui/stock/info.png', text='Info', id='info/'+p),
                                UI.TipIcon(icon='/dl/core/ui/stock/delete.png', text='Cancel', id='cancel/'+p),
                                spacing=0
                            ),
                    )
                tbl_pkgs.append(r)

        return ui

    def get_ui_info(self):
        pkg = self._info
        info = self.mgr.get_info(pkg)
        iui = self.mgr.get_info_ui(pkg)
        ui = UI.LT(
                UI.LTR(
                    UI.LTD(
                        UI.Image(file='/dl/pkgman/icon.png'),
                        rowspan=6
                    ),
                    UI.Label(text='Package:', bold=True),
                    UI.Label(text=pkg, bold=True)
                ),
                UI.LTR(
                    UI.Label(text='Installed:'),
                    UI.Label(text=info.installed)
                ),
                UI.LTR(
                    UI.Label(text='Available:'),
                    UI.Label(text=info.available)
                ),
                UI.LTR(
                    UI.Label(text='Description:'),
                    UI.Container(
                        UI.Label(text=info.description),
                        width=300
                    )
                ),
                UI.LTR(
                    UI.LTD(
                        iui,
                        colspan=2
                    )
                ),
                UI.LTR(
                    UI.LTD(
                        UI.HContainer(
                            UI.Button(text='(Re)install', id='install/'+pkg),
                            UI.Button(text='Remove', id='remove/'+pkg)
                        ),
                        colspan=2
                    )
                )
            )
        return UI.DialogBox(ui, id='dlgInfo')

    @event('tab/click')
    def on_li_click(self, event, params, vars=None):
        self._current = params[0]

    @event('button/click')
    @event('minibutton/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'refresh':
            self.mgr.refresh()
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
            self.mgr.mark_cancel_all(self._status)

    @event('dialog/submit')
    @event('form/submit')
    def on_dialog(self, event, params, vars=None):
        if params[0] == 'dlgApply':
            self._confirm_apply = False
            if vars.getvalue('action', '') == 'OK':
                self.mgr.apply(self._status)
                self._in_progress = True
        if params[0] == 'frmSearch':
            q = vars.getvalue('query','')
            if q != '':
                self._search = self.mgr.search(q, self._status)
            self._current = 'search'
        if params[0] == 'dlgInfo':
            self._info = None


class PackageManagerProgress(Plugin):
    implements(IProgressBoxProvider)
    title = 'Packages'
    icon = '/dl/pkgman/icon.png'
    can_abort = True

    def __init__(self):
        self.mgr = self.app.get_backend(apis.pkgman.IPackageManager)

    def has_progress(self):
        try:
            return self.mgr.is_busy()
        except:
            return False

    def get_progress(self):
        return self.mgr.get_busy_status()

    def abort(self):
        self.mgr.abort()
