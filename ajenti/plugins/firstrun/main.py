from ajenti.api import *
from ajenti import version
from ajenti.com import *
from ajenti.ui import *
from ajenti.utils import *


class FirstRun(CategoryPlugin, URLHandler):
    text = 'First run wizard'
    icon = None
    folder = None

    def on_session_start(self):
        self._step = 1
        
    def get_ui(self):
        ui = self.app.inflate('firstrun:main')
        step = self.app.inflate('firstrun:step%i'%self._step)
        ui.append('content', step)
        
        if self._step == 2:
            self._mgr = ajenti.plugmgr.PluginManager(self.app.config)        
            self._mgr.update_list()
            
            lst = self._mgr.available
            
            for k in lst:
                row = self.app.inflate('firstrun:item')
                row.find('name').set('text', k.name)
                row.find('desc').set('text', k.description)
                row.find('icon').set('file', k.icon)
                row.find('version').set('text', k.version)
                row.find('author').set('text', k.author)
                row.find('author').set('url', k.homepage)
                    
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
                
                row.find('check').set('name', 'install-'+k.id)
                if not ready:
                    row.append('reqs', UI.HelpIcon(text=req))

                ui.append('list', row)
            
        return ui

    @event('button/click')
    @event('minibutton/click')
    @event('linklabel/click')
    @event('form/submit')
    def on_event(self, event, params, vars=None):
        if params[0] == 'frmChangePassword':
            login = vars.getvalue('login', '')
            password = vars.getvalue('password', '')
            if login == '' or password == '':
                self.put_message('err', 'Enter valid login and password')
            else:
                self.config.remove_option('users', 'admin')
                self.config.set('users', login, hashpw(password))
                self.config.save()
                self._step = 2
        if params[0] == 'frmPlugins':
            lst = self._mgr.available
            
            for k in lst:
                if vars.getvalue('install-'+k.id, '0') == '1':
                    self._mgr.install(k.id)
            ComponentManager.get().rescan()
            
            self.config.set('ajenti', 'firstrun', 'no')
            self.config.save()
            self.put_message('info', 'Setup complete')
            self._step = 3
