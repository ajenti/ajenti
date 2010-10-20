from ajenti.api import *
from ajenti import version
from ajenti.com import *
from ajenti.ui import *
from ajenti.utils import *
import ajenti.plugmgr


class PluginManager(CategoryPlugin):
    text = 'Plugins'
    icon = '/dl/plugins/icon_small.png'
    folder = 'bottom'

    def on_session_start(self):
        self._tab = 0
        self._mgr = PluginManager(self.app)
        self._changes = False
        
    def get_ui(self):
        u = UI.PluginPanel(
                UI.Label(text='%s plugins active'%len(self._mgr.list_plugins())), 
                title='Plugins', 
                icon='/dl/plugins/icon.png'
            )

        tabs = UI.TabControl(active=self._tab)
        tabs.add('Installed', self.get_ui_installed())
        tabs.add('Available', self.get_ui_available())

        u.append(tabs)
        return u

    def get_ui_installed(self):
        lst = self._mgr.list_plugins()
        tbl = UI.LayoutTable()
        for k in lst:
            desc = '<span class="ui-el-label-1" style="padding-left: 5px;">%s</span>'%k.desc
            tbl.append(
                UI.LayoutTableRow(
                    UI.Image(file=k.icon),
                    UI.VContainer(
                        UI.Label(text='%s %s'%(k.name, k.version), size=3),
                        UI.OutLinkLabel(text='by '+k.author, url=k.homepage),
                        UI.Spacer(height=5),
                        UI.CustomHTML(html=desc),
                        UI.Spacer(height=5),
                        spacing=0
                    ),
                    UI.WarningMiniButton(
                        text='Uninstall', 
                        id='remove/'+k.id,
                        msg='Completely remove plugin "%s"'%k.name
                    )
                )
            ) 
            
        if self._changes or True:
            tbl = UI.VContainer(
                UI.Button(id='restart', text='Restart Ajenti for changes to take effect'),
                tbl,
                spacing=15
            )  
        return tbl

    def get_ui_available(self):
        lst = self._mgr.available
        inst = self._mgr.list_plugins()
        
        btn = UI.Button(text='Check for updates', id='update')
        if len(lst) == 0:
            btn['text'] = 'Download plugin list'
            
        tbl = UI.LayoutTable()
        for k in lst:
            same = False
            for p in inst: 
                if k['id'] == p.id and k['version'] == p.version: 
                    same = True
            if same:
                continue
            
            desc = '<span class="ui-el-label-1" style="padding-left: 5px;">%s</span>'%k['desc']
            tbl.append(
                UI.LayoutTableRow(
                    UI.Image(file=k['icon']),
                    UI.VContainer(
                        UI.Label(text='%s %s'%(k['name'], k['version']), size=3),
                        UI.OutLinkLabel(text='by '+k['author'], url=k['homepage']),
                        UI.Spacer(height=5),
                        UI.CustomHTML(html=desc),
                        UI.Spacer(height=5),
                        spacing=0
                    ),
                    UI.WarningMiniButton(
                        text='Install', 
                        id='install/'+k['id'],
                        msg='Download and install plugin "%s"'%k['name']
                    )
                )
            )   
        return UI.VContainer(btn, tbl, spacing=15)


    @event('button/click')
    @event('minibutton/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'update':
            self._tab = 1
            self._mgr.update_list()
        if params[0] == 'remove':
            self._tab = 0
            self._mgr.remove(params[1])
            self._changes = True
        if params[0] == 'restart':
            self.app.restart()
        if params[0] == 'install':
            self._tab = 0
            self._mgr.install(params[1])
            self._changes = True
        
    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        pass


class PluginsContent(ModuleContent):
    path = __file__
    module = 'plugins'    


class PluginManager(Plugin):
    def __init__(self):
        self.server = self.app.config.get('ajenti', 'update_server')
        self.available = []
        try:
            data = open('/var/lib/ajenti/plugins.list').read()
            self.available = eval(data)
        except:
            pass
            
    def list_plugins(self):
        res = []
        dir = self.app.config.get('ajenti', 'plugins')
        plugs = []
        plugs.extend(ajenti.plugmgr.loaded_plugins)
        plugs.extend(ajenti.plugmgr.disabled_plugins.keys())

        for k in plugs:
            i = PluginInfo()
            i.id = k
            i.icon = '/dl/%s/icon.png'%k
            m = ajenti.plugmgr.loaded_mods[k]
            i.name, i.desc, i.version = m.NAME, m.DESCRIPTION, m.VERSION
            i.author, i.homepage = m.AUTHOR, m.HOMEPAGE
            res.append(i)
        return res
        
    def update_list(self):        
        if not os.path.exists('/var/lib/ajenti'):
            os.mkdir('/var/lib/ajenti')
        data = shell('curl -sm 4 http://%s/plugins.php' % self.server)
        try:
            open('/var/lib/ajenti/plugins.list', 'w').write(data)
            self.available = eval(data)
        except:
            pass

    def remove(self, id):        
        dir = self.app.config.get('ajenti', 'plugins')
        shell('rm -r %s/%s' % (dir, id))

    def install(self, id):        
        dir = self.app.config.get('ajenti', 'plugins')
        self.remove(id)
                
        if shell_status('curl -sm 4 http://%s/plugins/%s/plugin.tar.gz -o %s/plugin.tar.gz' % (self.server, id, dir)):
            raise Exception()
            
        shell('cd %s; tar -xf plugin.tar.gz' % dir)
        shell('rm %s/plugin.tar.gz' % dir)
    
    
class PluginInfo:
    pass        
