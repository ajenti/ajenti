from ajenti.com import *
from ajenti.apis import API
from ajenti.app.helpers import CategoryPlugin, event
from ajenti.ui import UI
from ajenti import apis


class Webserver(API):
    
    class IWebserverBackend(Interface):
        def is_installed(self):
            return False

                    
    class WebserverPlugin(apis.services.ServiceControlPlugin):
        abstract = True
        
        ws_service = 'none'
        ws_title = 'none'
        ws_icon = 'none'
        ws_name = 'none'
        ws_backend = None

        def on_init(self):
            self.service_name = self.ws_service

        def on_session_start(self):
            self._backend = self.ws_backend
        
        def get_main_ui(self):
            panel = UI.ServicePluginPanel(title=self.ws_title, icon=self.ws_icon, status=self.service_status, servicename=self.service_name)

            if not self._backend.is_installed():
                panel.append(UI.VContainer(UI.ErrorBox(title='Error', text='%s is not installed'%self.ws_name)))
            else:
                panel.append(self.get_default_ui())

            return panel

        def get_default_ui(self):
            tc = UI.TabControl(active=self._tab)
            return tc

