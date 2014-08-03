import ajenti
from ajenti.api import *
from ajenti.plugins.webserver_common.api import WebserverPlugin
from ajenti.util import platform_select


@plugin
class Apache (WebserverPlugin):
    service_name = 'apache2'
    service_buttons = [
        {
            'command': 'force-reload',
            'text': _('Reload'),
            'icon': 'step-forward',
        }
    ]
    hosts_available_dir = platform_select(
        debian='/etc/apache2/sites-available',
        centos='/etc/httpd/conf.d',
        mageia='/etc/httpd/conf',
        freebsd='/usr/local/etc/apache/sites-available',
    )
    hosts_enabled_dir = '/etc/apache2/sites-enabled'
    supports_host_activation = platform_select(
        debian=True,
        default=False,
    )

    template = """<VirtualHost *:80>
    ServerAdmin webmaster@localhost

    DocumentRoot /var/www

    <Directory />
            Options FollowSymLinks
            AllowOverride None
    </Directory>

    <Directory /var/www/>
            Options Indexes FollowSymLinks MultiViews
            AllowOverride None
            Order allow,deny
            allow from all
    </Directory>
</VirtualHost>
"""

    def init(self):
        self.title = 'Apache'
        self.category = _('Software')
        self.icon = 'globe'
        if ajenti.platform in ['centos', 'mageia']:
            self.service_name = 'httpd'
