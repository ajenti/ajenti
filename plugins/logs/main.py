import gzip
import bz2

from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import *


class LogsPlugin(CategoryPlugin):
    text = 'Logs'
    icon = '/dl/logs/icon_small.png'
    folder = 'system'

    def on_session_start(self):
        self._log = ''
        self._tree = TreeManager()

    def get_ui(self):
        btn = None
        if self._file is not None:
            btn = UI.Button(text='Save', form='frmEdit', onclick='form', action='save')
        panel = UI.PluginPanel(UI.HContainer(UI.Label(text=self._log), btn), title='Log viewer', icon='/dl/logs/icon.png')
        panel.append(self.get_default_ui())
        return panel

    def get_default_ui(self):
        data = UI.LogViewer(width=500, height=500)
        if self._log != '':
            if self._log.endswith('.gz'):
                data = self.format_log(gzip.open(self._log).read())
            elif self._log.endswith('.bz2'):
                data = self.format_log(bz2.BZ2File(self._log, 'r').read())
            else:
                data = self.format_log(open(self._log).read())

        lt = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Label(text='Log files'),
                    UI.LayoutTableCell(
                        UI.LogFilter(),
                        float='right'
                    )
                ),
                UI.LayoutTableRow(
                    UI.ScrollContainer(self.get_ui_tree(), height=500),
                    data
                )
             )
        return lt

    def get_ui_tree(self):
        root = UI.TreeContainer(text='Logs', id='/')
        
        try:
            self.scan_logs(self.app.get_config(self).dir, root, '/')
        except:
            raise ConfigurationError('Can\'t read log tree')
            
        self._tree.apply(root)
        root['expanded'] = True
        return root

    def scan_logs(self, path, node, nodepath):
        dirs = os.listdir(path)
        dirs.sort()

        for x in dirs:
            try:
                if os.path.isdir(os.path.join(path, x)):
                    tn = UI.TreeContainer(text=x, id=nodepath+'/'+x)
                    node.append(tn)
                    self.scan_logs(os.path.join(path, x), tn, nodepath+'/'+x)
                else:
                    tn = UI.LinkLabel(text=fix_unicode(x), id='view/'+nodepath+'/'+fix_unicode(x))
                    tn = UI.TreeContainerNode(tn)
                    node.append(tn)
            except:
                pass


    def format_log(self, data):
        r = UI.LogViewer(width=500, height=500)
        d = '<span style="font-family: monospace">'
        d += enquote(data)
        d += '</span>'
        r.append(UI.CustomHTML(html=d))
        return r

    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'view':
            self._log = os.path.join(self.app.get_config(self).dir, *params[1:])

    @event('treecontainer/click')
    def on_tclick(self, event, params, vars=None):
        self._tree.node_click('/'.join(params))
        return ''
