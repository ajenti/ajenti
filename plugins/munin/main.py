from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import *
from ajenti import apis

from client import MuninClient
from widget import MuninWidget


class MuninPlugin(CategoryPlugin):
    text = 'Munin'
    icon = '/dl/munin/icon.png'
    folder = 'apps'

    def on_session_start(self):
        self._tree = TreeManager()
        self._host = None
        self._hist = None
        self._client = MuninClient(self.app)

    def get_ui(self):
        ui = self.app.inflate('munin:main')

        try:
            x = self._client.domains
        except Exception, e:
            raise ConfigurationError('Cannot reach Munin: ' + str(e))

        root = UI.TreeContainer(id='/', text='Hosts')

        for d in self._client.domains:
            t = UI.TreeContainer(
                id='/'+d.name,
                text=d.name,
                expanded=True,
            )
            for h in d.hosts:
                ll = UI.LinkLabel(
                    text=h.name,
                    id='view/%s/%s'%(d.name,h.name),
                )
                t.append(UI.TreeContainerNode(ll, active=(h==self._host)))
            root.append(t)

        ui.append('tree', root)
        self._tree.apply(root)
        root['expanded'] = True

        if self._hist is not None:
            ui.append('toolbar', UI.ToolButton(
                text='Close history',
                id='btnClose',
                icon='/dl/core/ui/stock/dialog-cancel.png',
            ))
            for p in ['Day', 'Week', 'Month', 'Year']:
                ui.append('main', UI.Container(
                    UI.Label(size=2, text=p),
                    UI.LinkLabel(text='Add widget', id='widget/%s'%p.lower()),
                ))
                ui.append('main', UI.Image(file=self._hist.history(p.lower())))
        elif self._host is not None:
            for g in self._host.graphs:
                ui.append('main', UI.HContainer(
                    UI.LinkLabel(text=g.full_name, id='history/%s'%g.name),
                    width='100%',
                ))
                ui.append('main', UI.Image(file=g.url))

        return ui

    @event('button/click')
    def on_button(self, event, params, vars=None):
        if params[0] == 'btnRefresh':
            self._client.reset()
        if params[0] == 'btnClose':
            self._hist = None

    @event('linklabel/click')
    def on_link(self, event, params, vars=None):
        if params[0] == 'view':
            ds = self._client.domains
            d = filter(lambda x:x.name==params[1], ds)[0]
            self._host = filter(lambda x:x.name==params[2], d.hosts)[0]
        if params[0] == 'history':
            self._hist = filter(lambda x:x.name==params[1], self._host.graphs)[0]
        if params[0] == 'widget':
            title = '%s on %s' % (self._hist.full_name, self._host.name)
            url = self._hist.history(params[1])
            cfg = { 'title': title, 'url': url }
            apis.dashboard.WidgetManager(self.app).add_widget(MuninWidget(self.app), cfg)
            self.put_message('info', 'Widget added')

    @event('treecontainer/click')
    def on_tclick(self, event, params, vars=None):
        self._tree.node_click('/'.join(params))
        return ''
