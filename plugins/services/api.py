from ajenti.com import *
from ajenti.apis import API
from ajenti.api import CategoryPlugin, event
from ajenti.ui import UI
from ajenti import apis


class Services(API):
    class IServiceManager(Interface):
        def list_all(self):
            pass

        def get_status(self, name):
            pass

        def start(self, name):
            pass

        def stop(self, name):
            pass

        def restart(self, name):
            pass


    class Service:
        name = ''
        status = ''

        def __cmp__(self, b):
            return 1 if self.name > b.name else -1

        def __str__(self):
            return self.name
            
    
    class ServiceControlPlugin(CategoryPlugin):
        abstract = True
        
        service_name = 'none'
        service_expected_status = None
        
        def get_ui(self):
            mgr = self.app.get_backend(apis.services.IServiceManager)
            
            st = 'failed'
            st = mgr.get_status(self.service_name)
            try:
                st = mgr.get_status(self.service_name)
                if self.service_expected_status:        
                    if self.service_expected_status != st:
                        st = 'failed'
            except:
                st = 'failed'

            self.service_status = st
            self.service_expected_status = None
            
            panel = UI.ServicePluginPanel(
                status=self.service_status, 
                servicename=self.service_name
            )
            return UI.Container(panel, self.get_main_ui())

        @event('servicecontrol/click')
        def on_service_control(self, event, params, vars=None):
            if params[0] == 'restart':
                mgr = self.app.get_backend(apis.services.IServiceManager)
                mgr.restart(self.service_name)
                self.service_expected_status = 'running'
            if params[0] == 'start':
                mgr = self.app.get_backend(apis.services.IServiceManager)
                mgr.start(self.service_name)
                self.service_expected_status = 'running'
            if params[0] == 'stop':
                mgr = self.app.get_backend(apis.services.IServiceManager)
                mgr.stop(self.service_name)
                self.service_expected_status = 'stopped'

