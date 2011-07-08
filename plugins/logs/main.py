import gzip
import bz2

from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import *


class LogsPlugin(CategoryPlugin):
    text = 'Logs'
    icon = '/dl/logs/icon.png'
    folder = 'system'

    def on_session_start(self):
        self._log = ''
        self._tree = TreeManager()

    def get_ui(self):
        ui = self.app.inflate('logs:main')
        data = None
        if self._log != '':
            if self._log.endswith('.gz'):
                data = self.format_log(gzip.open(self._log).read())
            elif self._log.endswith('.bz2'):
                data = self.format_log(bz2.BZ2File(self._log, 'r').read())
            else:
                data = self.format_log(open(self._log).read())
        ui.append('data', data)
        ui.append('tree', self.get_ui_tree())
        return ui

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
        d = '<span style="font-family: monospace">'
        d += enquote(data)
        d += '</span>'
        return UI.CustomHTML(html=d)

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
