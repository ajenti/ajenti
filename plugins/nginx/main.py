import os

from ajenti.com import *
from ajenti.app.helpers import ModuleContent
from ajenti import apis


class NginxBackend:
    config_dir = '/etc/nginx/'
    
    def is_installed(self):
        return os.path.exists(self.config_dir)
        

class NginxPlugin(apis.webserver.WebserverPlugin):
    text = 'nginx'
    icon = '/dl/nginx/icon_small.png'
    folder = 'servers'
    ws_service = 'nginx'
    ws_name = 'nginx'
    ws_icon = '/dl/nginx/icon.png'
    ws_title = 'nginx'
    ws_backend = NginxBackend()


class NginxContent(ModuleContent):
    module = 'nginx'
    path = __file__
