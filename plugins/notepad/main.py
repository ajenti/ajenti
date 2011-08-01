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
        self._roots = []
        self._files = []
        self._data = []
        self.add_tab()
        
        self._favs = []

        if self.app.config.has_option('notepad', 'favs'):
            self._favs = self.app.config.get('notepad', 'favs').split('|')

    def add_tab(self):
        self._tab = len(self._roots)
        self._roots.append(self.app.get_config(self).dir)
        self._files.append(None)
        self._data.append(None)
        
    def get_ui(self):
        mui = self.app.inflate('notepad:main')
        tabs = UI.TabControl(active=self._tab)
        mui.append('main', tabs)

        idx = 0        
        for root in self._roots:
            file = self._files[idx]
            data = self._data[idx]
            
            ui = self.app.inflate('notepad:tab')
            tabs.add(file or root, ui)
            
            favs = ui.find('favs')
            files = ui.find('files')
                
            for f in self._favs:
                files.append(
                    UI.ListItem(
                        UI.Image(file='/dl/core/ui/stock/bookmark.png'),
                        UI.Label(text=f), 
                        id='*'+str(self._favs.index(f))+'/%i'%idx,
                        active=f==file
                    )
                  )
            
            if root != '/':
                files.append(
                    UI.ListItem(
                        UI.Image(file='/dl/core/ui/stock/folder.png'),
                        UI.Label(text='..'), 
                        id='<back>/%i'%idx,
                        active=False,
                    )
                )

            for p in sorted(os.listdir(root)):
                path = os.path.join(root, p)
                if os.path.isdir(path):
                    files.append(
                        UI.ListItem(
                            UI.Image(file='/dl/core/ui/stock/folder.png'),
                            UI.Label(text=p), 
                            id=p+'/%i'%idx
                        )
                      )
                  
            for p in sorted(os.listdir(root)):
                path = os.path.join(root, p)
                if not os.path.isdir(path):
                    files.append(
                        UI.ListItem(
                            UI.Image(file='/dl/core/ui/stock/file.png'),
                            UI.Label(text=p), 
                            id=p+'/%i'%idx,
                            active=path==file
                        )
                      )

            ui.find('data').set('name', 'data/%i'%idx) 
            if file is not None:
                ui.find('data').set('value', data) 
            ui.find('data').set('id', 'data%i'%idx) 
        
            fbtn = ui.find('btnFav')
            ui.find('btnSave').set('action', 'save/%i'%idx)
            ui.find('btnClose').set('action', 'close/%i'%idx)
            if file is not None:
                if not file in self._favs:
                    fbtn.set('text', 'Bookmark')
                    fbtn.set('action', 'fav/%i'%idx)
                    fbtn.set('icon', '/dl/core/ui/stock/bookmark-add.png')
                else:
                    fbtn.set('text', 'Unbookmark')
                    fbtn.set('action', 'unfav/%i'%idx)
                    fbtn.set('icon', '/dl/core/ui/stock/bookmark-remove.png')
            else:
                ui.remove('btnSave')
                ui.remove('btnFav')
                if len(self._roots) == 1:
                    ui.remove('btnClose')

            idx += 1

        return mui
   
    @event('listitem/click')
    def on_list_click(self, event, params, vars=None):
        self._tab = int(params[1])
        if params[0] == '<back>':
            params[0] = '..'
        if params[0].startswith('*'):
            params[0] = self._favs[int(params[0][1:])]
            
        p = os.path.abspath(os.path.join(self._roots[self._tab], params[0]))
        if os.path.isdir(p):
            self._roots[self._tab] = p
        else:
            try:
                data = open(p).read()        
                self._files[self._tab] = p
                self._data[self._tab] = data
            except:
                self.put_message('warn', 'Cannot open %s'%p)

    @event('button/click')
    def on_button(self, event, params, vars=None):
        if params[0] == 'btnClose':
            self._file = None
            
    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        if vars.getvalue('action', None) == 'newtab':
            self.add_tab()
            
        for idx in range(0,len(self._roots)):
            if idx >= len(self._roots): # closed
                break
                
            self._data[idx] = vars.getvalue('data/%i'%idx, None)
            if vars.getvalue('action', None) == 'save/%i'%idx:
                self._tab = idx
                if self._files[idx] is not None:
                    open(self._files[idx], 'w').write(self._data[idx])
                    self.put_message('info', 'Saved')
            if vars.getvalue('action', '') == 'fav/%i'%idx:
                self._tab = idx
                self._favs.append(self._files[idx])
            if vars.getvalue('action', '') == 'unfav/%i'%idx:
                self._tab = idx
                self._favs.remove(self._files[idx])
            if vars.getvalue('action', '') == 'close/%i'%idx:
                self._tab = 0
                del self._roots[idx]
                del self._files[idx]                
                del self._data[idx]                
                if len(self._roots) == 0:
                    self.add_tab()
            self.app.config.set('notepad', 'favs', '|'.join(self._favs))
            self.app.config.save()
            
            
