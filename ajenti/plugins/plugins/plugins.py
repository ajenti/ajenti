import ajenti
from ajenti.api import *
from ajenti.plugins import manager
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder


@plugin
class PluginsPlugin (SectionPlugin):
    def init(self):
        self.title = 'Plugins'
        self.icon = 'cogs'
        self.category = ''
        self.order = 50

        # In case you didn't notice it yet, this is the Plugins Plugin
        self.append(self.ui.inflate('plugins:main'))

        self.binder = Binder(self, self.find('plugins'))

        """
        self.find('users').new_item = lambda c: UserData()

        def post_user_bind(object, collection, item, ui):
            box = ui.find('permissions')
            for prov in PermissionProvider.get_all():
                line = self.ui.create('tab', title=prov.get_name())
                box.append(line)
                for perm in prov.get_permissions():
                    line.append(self.ui.create('checkbox', id=perm[0], text=perm[1], \
                        value=(perm[0] in item.permissions)))
        self.find('users').post_item_bind = post_user_bind
        """

        self.refresh()

    def refresh(self):
        self.plugins = sorted(manager.get_all().values())
        self.binder.reset().autodiscover().populate()
