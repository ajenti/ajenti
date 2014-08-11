from ajenti.api import *
from ajenti.plugins.webserver_common.api import WebserverPlugin
from ajenti.util import platform_select


@plugin
class Nginx(WebserverPlugin):
    platforms = ['debian', 'centos', 'freebsd', 'arch', 'mageia']
    service_name = 'nginx'
    service_buttons = [
        {
            'command': 'force-reload',
            'text': _('Reload'),
            'icon': 'step-forward',
        }
    ]
    hosts_available_dir = platform_select(
        debian='/etc/nginx/sites-available',
        centos='/etc/nginx/conf.d',
        mageia='/etc/nginx/conf.d',
        freebsd='/usr/local/etc/nginx/conf.d',
        arch='/etc/nginx/sites-available',
    )
    hosts_enabled_dir = '/etc/nginx/sites-enabled'
    supports_host_activation = platform_select(
        debian=True,
        arch=True,
        default=False,
    )

    configurable = True
    main_conf_files = platform_select(
        debian=['/etc/nginx/nginx.conf', '/etc/nginx/proxy_params', '/etc/nginx/fastcgi_params',
                '/etc/nginx/scgi_params', '/etc/nginx/uwsgi_params'],
        centos=['/etc/nginx/nginx.conf', '/etc/nginx/fastcgi_params',
                '/etc/nginx/scgi_params', '/etc/nginx/uwsgi_params'],
        default=[],
    )

    template = """server {
    server_name name;
    access_log /var/log/nginx/name.access.log;
    error_log  /var/log/nginx/name.error.log;

    listen 80;

    location / {
        root /var/www/name;
    }

    location ~ \.lang$ {
        include fastcgi_params;
        fastcgi_pass 127.0.0.1:port;
        fastcgi_split_path_info ^()(.*)$;
    }
}
"""

    def init(self):
        self.title = 'NGINX'
        self.category = _('Software')
        self.icon = 'globe'
