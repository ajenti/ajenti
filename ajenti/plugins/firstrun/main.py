from ajenti.api import *
from ajenti import version
from ajenti.com import *
from ajenti.ui import *
from ajenti.utils import *
from ajenti.plugmgr import RepositoryManager

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
            self._mgr = RepositoryManager(self.app.config)
            self._mgr.update_list()

            lst = self._mgr.available

            for k in sorted(lst, key=lambda x:x.name):
                row = self.app.inflate('firstrun:item')
                row.find('name').set('text', k.name)
                row.find('desc').set('text', k.description)
                row.find('icon').set('file', k.icon)
                row.find('version').set('text', k.version)
                row.find('author').set('text', k.author)
                row.find('author').set('url', k.homepage)

                req = k.str_req()

                row.find('check').set('name', 'install-'+k.id)
                if req != '':
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
                self.app.gconfig.remove_option('users', 'admin')
                self.app.gconfig.set('users', login, hashpw(password))
                self.app.gconfig.save()
                self._step = 2
        if params[0] == 'frmPlugins':
            lst = self._mgr.available

            for k in lst:
                if vars.getvalue('install-'+k.id, '0') == '1':
                    try:
                        self._mgr.install(k.id)
                    except:
                        pass
            ComponentManager.get().rescan()

            self.app.gconfig.set('ajenti', 'firstrun', 'no')
            self.app.gconfig.save()
            self.put_message('info', 'Setup complete')
            self._step = 3
