import ajenti
from ajenti.api import *
from ajenti.plugins.webserver_common.api import WebserverPlugin
from ajenti.util import platform_select


@plugin
class Apache(WebserverPlugin):
    service_name = platform_select(
        default='apache2',
        osx='org.macports.apache2'
    )
    service_buttons = [
        {
            'command': 'force-reload',
            'text': _('Reload'),
            'icon': 'reload',
        }
    ]
    hosts_available_dir = platform_select(
        debian='/etc/apache2/sites-available',
        centos='/etc/httpd/conf.d',
        mageia='/etc/httpd/conf',
        freebsd='/usr/local/etc/apache/sites-available',
        osx='/opt/local/apache2/conf',
    )
    hosts_enabled_dir = platform_select(
        debian='/etc/apache2/sites-enabled',
        freebsd='/usr/local/etc/apache/sites-enabled'
    )
    supports_host_activation = platform_select(
        debian=True,
        freebsd=True,
        default=False,
    )

    configurable = True
    main_conf_files = platform_select(
        debian=['/etc/apache2/apache2.conf', '/etc/apache2/ports.conf', '/etc/apache2/envvars', '/etc/apache2/magic'],
        centos=['/etc/httpd/conf/httpd.conf', '/etc/httpd/conf/magic'],
        default=[],
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
