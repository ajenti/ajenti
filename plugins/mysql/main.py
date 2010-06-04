from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *

from api import *


class MySQL(CategoryPlugin):
    implements((ICategoryProvider, 60))

    text = 'DB Server'
    description = 'Manage databases'
    icon = '/dl/mysql/icon.png'

    backends = None
    backend = None
    
    def on_init(self):
        self._logging_in = not self.config.has_option('mysql', 'backend')
        self.backends = [b.name for b in self.app.grab_plugins(IDBBackend)] 
        if self.config.has_option('mysql', 'backend'):
            self.backend = self.app.grab_plugins(IDBBackend, 
                            lambda x: x.name == self.config.get('mysql', 'backend'))[0]
            
    def on_session_start(self):
        self._labeltext = ''
        self._logging_in = False
        self._tab = 0
        self._sql = ''

    def get_ui(self):
        self.on_init()
        
        h = UI.HContainer(
               UI.Image(file='/dl/mysql/bigicon.png'),
               UI.Spacer(width=10),
               UI.VContainer(
                   UI.Label(text='Database server', size=5),
                   UI.Button(text='Reconnect', id='btnLogout')
               )
            )

        lstBends = UI.Select(name='backend')
        for b in self.backends:
            lstBends.appendChild(UI.SelectOption(value=b, text=b))
            
        dlgLogin = UI.DialogBox(
                        UI.LayoutTable(
                            UI.LayoutTableRow(
                                UI.Label(text='Backend:'),
                                lstBends
                            ),
                            UI.LayoutTableRow(
                                UI.Label(text='Host:'),
                                UI.TextInput(name='host', value='localhost')
                            ),
                            UI.LayoutTableRow(
                                UI.Label(text='Login:'),
                                UI.TextInput(name='login', value='root')
                            ),
                            UI.LayoutTableRow(
                                UI.Label(text='Password:'),
                                UI.TextInput(name='passwd', value='')
                            ),
                            UI.LayoutTableRow(
                                UI.Label(text='Database:'),
                                UI.TextInput(name='db', value='')
                            )
                        ),
                        title="SQL server connection", id="dlgLogin", action="/handle/dialog/submit/dlgLogin"
                    )

        tblTables = UI.DataTable(
                        UI.DataTableRow(
                            UI.Label(text='Name', width=200),
                            UI.Label(text='Controls', width=200),
                            header = True
                        )
                    )


        tsql = None
        if not self._logging_in:
            try:
                self.backend.connect(
                    self.config.get('mysql', 'host'),
                    self.config.get('mysql', 'login'),
                    self.config.get('mysql', 'passwd'),
                    self.config.get('mysql', 'db')
                )
            except Exception as e:
                return UI.VContainer(h, UI.ErrorBox(title='Error', text='Connection problem: ' + str(e)))
            
            t = self.backend.sql('SHOW TABLES;')
            for r in t:
                row = UI.DataTableRow(
                        UI.Label(text=r[0]),
                        UI.LinkLabel(text='View', id=('view/'+r[0]))
                      )
                tblTables.appendChild(row)

            tsql = UI.DataTable()
            if self._tab == 1 and len(self._sql)>0:
                if self._sql[-1] != ';': self._sql += ';'
                data = self.backend.sql(self._sql)
                if data == None:
                    tsql = UI.ErrorBox(title='SQL', text='Invalid query')
                else:
                    for row in data:
                        r = UI.DataTableRow()
                        for f in row:
                            r.appendChild(UI.DataTableCell(UI.Label(text=str(f))))
                        tsql.appendChild(r)
    
            self.backend.disconnect()


        
        cntSQL = UI.VContainer(
                UI.HContainer(
                    UI.Form(
                        UI.HContainer(
                            UI.TextInput(name='query', size=70, value=self._sql),
                            UI.Button(text='Execute', onclick='form', form='frmSQL')
                        ),
                        id='frmSQL',
                        action='/handle/dialog/submit/frmSQL'
                    )
                ),
                UI.Spacer(height=20),
                tsql
             )
                    
        t = UI.TabControl(active=self._tab)
        t.add('Tables', tblTables)
        t.add('SQL', cntSQL)
        
        p = UI.VContainer(
                h,
                UI.Spacer(height=20),
                t,
                dlgLogin if self._logging_in else None
            )

        return p

    def logout(self):
        self.config.remove_option('mysql', 'login')
        self.config.remove_option('mysql', 'host')
        self.config.remove_option('mysql', 'passwd')
        self.config.remove_option('mysql', 'db')
        self.config.remove_option('mysql', 'backend')
        self.config.save()    

    def login(self, vars):
        self.config.set('mysql', 'backend', vars.getvalue('backend', 'mysql'))        
        self.config.set('mysql', 'host', vars.getvalue('host', 'localhost'))        
        self.config.set('mysql', 'login', vars.getvalue('login', 'root'))        
        self.config.set('mysql', 'passwd', vars.getvalue('passwd', '')) # plaintext!        
        self.config.set('mysql', 'db', vars.getvalue('db', ''))   
        self.config.save()    

    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'btnLogout':
            self.logout()
        if params[0] == 'view':
            self._tab = 1
            self._sql = 'SELECT * FROM %s;' % params[1]
            
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        if params[0] == 'dlgLogin':
            if vars.getvalue('action', '') == 'OK':
                self.login(vars)
            self._logging_in = False    
        if params[0] == 'frmSQL':
            self._tab = 1
            self._sql = vars.getvalue('query', '')


class MySQLContent(ModuleContent):
    module = 'mysql'
    path = __file__
    
