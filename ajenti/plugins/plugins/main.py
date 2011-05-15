from ajenti.api import *
from ajenti import version
from ajenti.com import *
from ajenti.ui import *
from ajenti.utils import *

import ajenti.plugmgr


class PluginManager(CategoryPlugin, URLHandler):
    text = 'Plugins'
    icon = '/dl/plugins/icon_small.png'
    folder = 'bottom'

    def on_session_start(self):
        self._tab = 0
        self._mgr = ajenti.plugmgr.PluginManager(self.app.config)
        self._changes = False
        
    def get_ui(self):
        ui = self.app.inflate('plugins:main')
        
        inst = self._mgr.installed

        for k in inst:
            row = self.app.inflate('plugins:item')
            desc = '<span class="ui-el-label-1" style="padding-left: 5px;">%s</span>'%k.desc
            row.find('name').set('text', k.name)
            row.find('desc').set('text', k.desc)
            row.find('icon').set('file', k.icon)
            row.find('version').set('text', k.version)
            row.find('author').set('text', k.author)
            row.find('author').set('url', k.homepage)
            row.append('buttons', UI.WarningMiniButton(
                        text='Uninstall', 
                        id='remove/'+k.id,
                        msg='Completely remove plugin "%s"'%k.name
                    ))
                    
            if k.problem:
                row.find('status').set('file', '/dl/plugins/broken.png')
                row.append('reqs', UI.HelpIcon(text=k.problem))
            else:
                row.find('status').set('file', '/dl/plugins/good.png')
            ui.append('list', row)
            
                
        lst = self._mgr.available
        
        btn = UI.Button(text='Check for updates', id='update')
        if len(lst) == 0:
            btn['text'] = 'Download plugin list'
            
        for k in lst:
            row = self.app.inflate('plugins:item')
            row.find('name').set('text', k.name)
            row.find('desc').set('text', k.description)
            row.find('icon').set('file', k.icon)
            row.find('version').set('text', k.version)
            row.find('author').set('text', k.author)
            row.find('author').set('url', k.homepage)
                    
            row.find('status').set('file', '/dl/plugins/none.png')
            for p in inst: 
                if k.id == p.id and not p.problem:
                    row.find('status').set('file', '/dl/plugins/upgrade.png')

            reqd = ajenti.plugmgr.get_deps(self.app.platform, k.deps)

            req = 'Requires: '
                  
            ready = True      
            for r in reqd:
                if ajenti.plugmgr.verify_dep(r):
                    continue
                if r[0] == 'app':
                    req += 'application %s (%s); '%r[1:]
                if r[0] == 'plugin':
                    req += 'plugin %s; '%r[1]
                ready = False    
                    
            url = 'http://%s/view/plugins.php?id=%s' % (
                    self.app.config.get('ajenti', 'update_server'),
                    k.id
                   )

            if ready:
                row.append('buttons', UI.WarningMiniButton(
                        text='Install', 
                        id='install/'+k.id,
                        msg='Download and install plugin "%s"'%k.name
                    ))
            else:
                row.append('reqs', UI.HelpIcon(text=req))

            ui.append('list', row)

        return ui

    def get_ui_upload(self):
        return UI.Uploader(
            url='/upload_plugin',
            text='Install'
        )
    
    @url('^/upload_plugin$')
    def upload(self, req, sr):
        vars = get_environment_vars(req)
        f = vars.getvalue('file', None)
        try:
            self._mgr.install_stream(f)
        except:
            pass
        sr('301 Moved Permanently', [('Location', '/')])
        self._changes = True
        return ''
        
    @event('button/click')
    @event('minibutton/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'update':
            self._tab = 1
            self._mgr.update_list()
            self.put_message('info', 'Plugin list updated')
        if params[0] == 'remove':
            self._tab = 0
            self._mgr.remove(params[1])
            self._changes = True
            self.put_message('warn', 'Plugin removed. Restart Ajenti for changes to take effect.')
        if params[0] == 'restart':
            self.app.restart()
        if params[0] == 'install':
            self._tab = 0
            self.put_message('info', 'Plugin installed. Refresh page for changes to take effect.')
            self._mgr.install(params[1])
            ComponentManager.get().rescan()
            
        
