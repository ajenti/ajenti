from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import shell, enquote, BackgroundProcess
from ajenti.plugins.core.api import *
from ajenti.utils import *

from ajenti import plugmgr


class TestsPlugin(CategoryPlugin):
    text = 'Tests'
    icon = '/dl/tests/icon.png'
    folder = 'apps'

    def get_ui(self):
        ui = self.app.inflate('tests:main')
        ui.find('result').set('text', 'Passed' if self.test() else 'Failed: %s' % self.err)
        return ui
        
    def test(self):
        users = plugmgr.loaded_mods['users'].backend.UsersBackend(self.app)
        res = True
        
        try:
            lst = users.add_user('ajentitestuser')
        except:
            res = False
            self.err = 'Cant add user'

        try:
            users.get_user('ajentitestuser', users.get_all_users())
        except:
            res = False
            self.err = 'User wasnt added'
            
        try:
            users.del_user('ajentitestuser')
        except:
            res = False
            self.err = 'Cant delete user'

        try:
            users.get_user('ajentitestuser', users.get_all_users())
            res = False
            self.err = 'User wasnt deleted'
        except:
            pass
            
        return res   
            

                            
