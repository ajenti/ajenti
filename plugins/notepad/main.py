from ajenti.ui import *
from ajenti.com import implements
from ajenti.api import *
from ajenti.utils import shell, enquote, BackgroundProcess
from ajenti.plugins.core.api import *
from ajenti.utils import *


class NotepadPlugin(CategoryPlugin):
    text = 'Notepad'
    icon = '/dl/notepad/icon.png'
    folder = 'tools'

    def on_session_start(self):
        self._root = self.app.get_config(self).dir
        self._file = None
        self._favs = []
        if self.app.config.has_option('notepad', 'favs'):
            self._favs = self.app.config.get('notepad', 'favs').split('|')

        
    def get_ui(self):
        ui = self.app.inflate('notepad:main')
            
        favs = ui.find('favs')
        files = ui.find('files')
                
        for f in self._favs:
            favs.append(
                UI.ListItem(
                    UI.Label(text=f), 
                    id='*'+str(self._favs.index(f)),
                    active=f==self._file
                )
              )
            
        if self._root != '/':
            files.append(
                UI.ListItem(
                    UI.Image(file='/dl/core/ui/stock/folder.png'),
                    UI.Label(text='..'), 
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

        if self._file is not None:
            data = ''
            try:
                data = open(self._file).read()        
                ui.find('data').set('value', data) 
            except:
                self.put_message('warn', 'Cannot open %s'%self._file)
                self._file = None
        
        fbtn = ui.find('btnFav')
        if self._file is not None:
            if not self._file in self._favs:
                fbtn.set('text', 'Bookmark')
                fbtn.set('action', 'fav')
            else:
                fbtn.set('text', 'Unbookmark')
                fbtn.set('action', 'unfav')
        else:
            ui.remove('btnSave')
            ui.remove('btnFav')
            ui.remove('btnClose')

        return ui
   
    @event('listitem/click')
    def on_list_click(self, event, params, vars=None):
        if params[0] == '<back>':
            params[0] = '..'
        if params[0].startswith('*'):
            params[0] = self._favs[int(params[0][1:])]
        p = os.path.abspath(os.path.join(self._root, params[0]))
        if os.path.isdir(p):
            self._root = p
        else:
            self._file = p

    @event('button/click')
    def on_button(self, event, params, vars=None):
        if params[0] == 'btnClose':
            self._file = None
            
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        text = vars.getvalue('text', None)
        if text is not None:
            open(self._file, 'w').write(text)
            self.put_message('info', 'Saved')
            if vars.getvalue('action', '') == 'fav':
                self._favs.append(self._file)
            if vars.getvalue('action', '') == 'unfav':
                self._favs.remove(self._file)
            self.app.config.set('notepad', 'favs', '|'.join(self._favs))
            self.app.config.save()
            
            
