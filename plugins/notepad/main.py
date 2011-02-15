from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import shell, enquote, BackgroundProcess
from ajenti.plugins.core.api import *
from ajenti.utils import *


class NotepadPlugin(CategoryPlugin):
    text = 'Notepad'
    icon = '/dl/notepad/icon_small.png'
    folder = 'tools'

    def on_session_start(self):
        self._root = self.app.get_config(self).dir
        self._file = None
        
    def get_ui(self):
        btn = None
        if self._file is not None:
            btn = UI.Button(text='Save', form='frmEdit', onclick='form', action='save')
        panel = UI.PluginPanel(
                    UI.VContainer(
                        UI.Label(text=(self._file or self._root)), 
                        btn
                    ),
                    title='Notepad',
                    icon='/dl/notepad/icon.png'
                )
        panel.append(self.get_default_ui())
        return panel

    def get_default_ui(self):
        files = UI.List(width=200, height=400)
                
        if self._root != '/':
            files.append(
                UI.ListItem(
                    UI.Image(file='/dl/core/ui/stock/folder.png'),
                    UI.Label(text='Up one level'), 
                    id='<back>',
                    active=False,
                )
            )

        for p in sorted(os.listdir(self._root)):
            path = os.path.join(self._root, p)
            if os.path.isdir(path):
                files.append(
                    UI.ListItem(
                        UI.Image(file='/dl/core/ui/stock/folder.png'),
                        UI.Label(text=p), 
                        id=p,
                        active=path==self._file
                    )
                  )
                  
        for p in sorted(os.listdir(self._root)):
            path = os.path.join(self._root, p)
            if not os.path.isdir(path):
                files.append(
                    UI.ListItem(
                        UI.Label(text=p), 
                        id=p,
                        active=path==self._file
                    )
                  )

        edit = None
        if self._file is not None:
            area = UI.TextInputArea(
                width=530, 
                height=400, 
                value=open(self._file).read(), 
                name='text',
            )    
            btn = UI.Button(text='Save', action='OK')
            edit = UI.FormBox(
                area,
                width=530, height=450,
                id='frmEdit', right=True,
                hideok=True, hidecancel=True,
                miscbtn='Save', miscbtnid='save',
            )    
        
        t = UI.HContainer(files, edit, spacing=10)
        return t
   
    @event('listitem/click')
    def on_list_click(self, event, params, vars=None):
        if params[0] == '<back>':
            params[0] = '..'
        p = os.path.abspath(os.path.join(self._root, params[0]))
        if os.path.isdir(p):
            self._root = p
        else:
            self._file = p

    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        text = vars.getvalue('text', None)
        print text, params
        if text is not None:
            open(self._file, 'w').write(text)
            self.put_message('info', 'Saved')
                   
