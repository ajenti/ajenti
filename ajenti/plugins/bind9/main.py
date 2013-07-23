import os

from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

from reconfigure.configs import BIND9Config
from reconfigure.items.bind9 import ZoneData


@plugin
class BIND9Plugin (SectionPlugin):
    def init(self):
        self.title = 'BIND9'
        self.icon = 'globe'
        self.category = _('Software')

        self.append(self.ui.inflate('bind9:main'))

        self.config = BIND9Config(path='/etc/bind/named.conf')
        self.binder = Binder(None, self)
        self.find('zones').new_item = lambda c: ZoneData()

        def post_zone_bind(o, c, i, u):
            path = i.file
            if not path.startswith('/'):
                path = '/etc/bind/' + path
            exists = os.path.exists(path)
            u.find('no-file').visible = not exists
            u.find('file').visible = exists
            if exists:
                u.find('editor').value = open(path).read()

            def on_save_zone():
                open(path, 'w').write(u.find('editor').value)
                self.context.notify('info', _('Zone saved'))

            def on_create_zone():
                open(path, 'w').write("""
                    $TTL    604800
@       IN      SOA     ns. root.ns. (
                              1         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@                   IN      NS      ns.
example.com.        IN      A       127.0.0.1
example.com.        IN      AAAA    ::1
""")
                u.find('no-file').visible = not exists
                u.find('file').visible = True
                u.find('no-file').value = False

            u.find('save-zone').on('click', on_save_zone)
            u.find('create-zone').on('click', on_create_zone)
        self.find('zones').post_item_bind = post_zone_bind

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.config.load()
        self.binder.reset(self.config.tree).autodiscover().populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.config.save()
        self.refresh()
        self.context.notify('info', _('Saved'))
