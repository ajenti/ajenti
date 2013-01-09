from ajenti.api import *
from ajenti.plugins.webserver_common.api import WebserverPlugin


@plugin
class Nginx (WebserverPlugin):
    service_name = 'nginx'
    service_buttons = [
        {
            'command': 'force-reload',
            'text': 'Reload',
            'icon': 'step-forward',
        }
    ]
    hosts_available_dir = '/etc/nginx/sites-available'
    hosts_enabled_dir = '/etc/nginx/sites-enabled'

    def init(self):
        self.title = 'nginx'
        self.category = 'Software'
        self.icon = 'globe'
