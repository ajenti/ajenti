import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui.binder import Binder
from ajenti.users import UserManager
from reconfigure.items.ajenti import User


@plugin
class Configurator (SectionPlugin):
    def init(self):
        self.title = 'Configure'
        self.category = 'Ajenti'
        self.order = 50

        self.append(self.ui.inflate('configurator:main'))

        self.binder = Binder(ajenti.config.tree, self.find('ajenti-config'))
        self.find('users').new_item = lambda c: User('Unnamed', '')
        self.binder.autodiscover()
        self.binder.populate()

        self.find('save-button').on('click', self.save)

    def save(self):
        self.binder.update()
        for user in ajenti.config.tree.users.values():
            user.password = UserManager.get().hash_password(user.password)
        self.binder.populate()
        ajenti.config.save()
        self.publish()
