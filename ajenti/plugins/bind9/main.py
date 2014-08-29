import os

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder
from ajenti.util import platform_select

from reconfigure.configs import BIND9Config
from reconfigure.items.bind9 import ZoneData


@plugin
class BIND9Plugin (SectionPlugin):
    config_root = platform_select(
        debian='/etc/bind/',
        centos='/etc/named/',
        mageia='/etc/named/',
        arch='/var/named/',
    )

    config_path = platform_select(
        debian='/etc/bind/named.conf',
        default='/etc/named.conf',
    )

    def init(self):
        self.title = 'BIND9'
        self.icon = 'globe'
        self.category = _('Software')

        self.append(self.ui.inflate('bind9:main'))

        self.config = BIND9Config(path=self.config_path)
        self.binder = Binder(None, self)
        self.find('zones').new_item = lambda c: ZoneData()

        def post_zone_bind(o, c, item, u):
            path = item.file
            if path is not None:
                if not path.startswith('/'):
                    path = self.config_root + path
                exists = os.path.exists(path)
            else:
                exists = False
            u.find('no-file').visible = not exists
            u.find('file').visible = exists
            if exists:
                u.find('editor').value = open(path).read()

            def on_save_zone():
                open(path, 'w').write(u.find('editor').value)
                self.context.notify('info', _('Zone saved'))

            def on_create_zone():
                self.binder.update()
                open(path, 'w').write("""$TTL    604800
@       IN      SOA     ns. root.ns. (
                              1         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@                   IN      NS      ns.
%(name)s.        IN      A       127.0.0.1
%(name)s.        IN      AAAA    ::1
""" % {'name': item.name})
                post_zone_bind(o, c, item, u)

            u.find('save-zone').on('click', on_save_zone)
            u.find('create-zone').on('click', on_create_zone)
        self.find('zones').post_item_bind = post_zone_bind

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self.binder.setup(self.config.tree).populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
        self.refresh()
        self.context.notify('info', _('Saved'))
