from ajenti.api import *
from ajenti import version
from ajenti.com import *
from ajenti.ui import *
import ajenti.plugmgr


class PluginManager(CategoryPlugin):
    text = 'Plugins'
    icon = '/dl/plugins/icon_small.png'
    folder = 'bottom'

    def on_session_start(self):
        self._tab = 0
        self._mgr = PluginManager(self.app)

    def get_ui(self):
        u = UI.PluginPanel(
                UI.Label(text='%s plugins active'%len(self._mgr.list_plugins())), 
                title='Plugins', 
                icon='/dl/plugins/icon.png'
            )

        tabs = UI.TabControl(active=self._tab)
        tabs.add('General', self.get_ui_general())

        u.append(tabs)
        return u

    def get_ui_general(self):
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
        return tbl


    @event('button/click')
    @event('minibutton/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        pass
        
    @event('form/submit')
    @event('dialog/submit')
    def on_submit(self, event, params, vars=None):
        pass


class PluginsContent(ModuleContent):
    path = __file__
    module = 'plugins'    


class PluginManager(Plugin):
    def list_plugins(self):
        res = []
        dir = self.app.config.get('ajenti', 'plugins')
        for k in ajenti.plugmgr.loaded_plugins:
            i = PluginInfo()
            i.id = k
            i.icon = '/dl/%s/icon.png'%k
            m = ajenti.plugmgr.loaded_mods[k]
            i.name, i.desc, i.version = m.NAME, m.DESCRIPTION, m.VERSION
            i.author, i.homepage = m.AUTHOR, m.HOMEPAGE
            res.append(i)
        return res
        
class PluginInfo:
    pass        
