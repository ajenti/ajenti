from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *
from ajenti.utils import *

import gzip


class LogsPlugin(CategoryPlugin):
    implements((ICategoryProvider, 60))

    text = 'Logs'
    icon = '/dl/logs/icon.png'
        
    def on_session_start(self):
        self._log = ''
        self._tree = TreeManager()
        
    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(text=self._log), title='Log viewer', icon='/dl/logs/icon.png')

        panel.appendChild(self.get_default_ui())        

        return panel

    def get_default_ui(self):
        data = UI.LogViewer(width=600, height=500)
        if self._log != '':
            if self._log.endswith('.gz'):
                data = self.format_log(gzip.open(self._log).read())
            else:
                data = self.format_log(open(self._log).read())
            
        lt = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.ScrollContainer(self.get_ui_tree(), height=500),
                    data
                )
             )
        return lt

    def get_ui_tree(self):
        root = UI.TreeContainer(text='Logs', id='/')
        self.scan_logs('/var/log', root, '/')
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
                    node.appendChild(tn)
                    self.scan_logs(os.path.join(path, x), tn, nodepath+'/'+x)
                else:        
                    tn = UI.LinkLabel(text=fix_unicode(x), id='view/'+nodepath+'/'+fix_unicode(x))        
                    tn = UI.TreeContainerNode(tn)
                    node.appendChild(tn)
            except:
                pass
            

    def format_log(self, data):
        r = UI.LogViewer(width=600, height=500)
        for s in data.split('\n'):
            r.appendChild(UI.LogViewerLine(text=s))
        return r
        
    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'view':
            self._log = os.path.normpath('/var/log/' + '/'.join(params[1:]))

    @event('treecontainer/click')
    def on_tclick(self, event, params, vars=None):
        self._tree.node_click('/'.join(params))
        return ''
       
"""   @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                if self._editing == 'adduser':
                    backend.add_user(v)
                    self._selected_user = v
                if self._editing == 'addgrp':
                    backend.add_group(v)
                    self._selected_group = v
                if self._editing == 'login':
                    backend.change_user_login(self._selected_user, v)
                    self._selected_user = v
                if self._editing == 'uid':
                    backend.change_user_uid(self._selected_user, v)
                if self._editing == 'gid':
                    backend.change_user_gid(self._selected_user, v)
                if self._editing == 'shell':
                    backend.change_user_shell(self._selected_user, v)
                if self._editing == 'password':
                    backend.change_user_password(self._selected_user, v)
                if self._editing == 'home':
                    backend.change_user_home(self._selected_user, v)
                if self._editing == 'name':
                    backend.change_group_name(self._selected_group, v)
                    self._selected_group = v
                if self._editing == 'ggid':
                    backend.change_group_gid(self._selected_group, v)
            self._editing = '' 
        if params[0] == 'dlgEditUser':
            self._selected_user = '' 
        if params[0] == 'dlgEditGroup':
            self._selected_group = '' 
"""
        
class LogsContent(ModuleContent):
    module = 'logs'
    path = __file__
    widget_files = ['logviewer.xml']
    css_files = ['logviewer.css']
    
    
