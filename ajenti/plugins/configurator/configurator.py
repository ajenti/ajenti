import os
import subprocess

import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin, intent
from ajenti.ui import on
from ajenti.ui.binder import Binder
from ajenti.users import UserManager, PermissionProvider, restrict
from reconfigure.items.ajenti import UserData


@plugin
class Configurator (SectionPlugin):
    def init(self):
        self.title = 'Configure'
        self.icon = 'wrench'
        self.category = ''
        self.order = 50

        self.append(self.ui.inflate('configurator:main'))

        self.binder = Binder(ajenti.config.tree, self.find('ajenti-config'))
        self.find('users').new_item = lambda c: UserData()

        def post_user_bind(object, collection, item, ui):
            box = ui.find('permissions')
            box.empty()
            for prov in PermissionProvider.get_all():
                line = self.ui.create('tab', title=prov.get_name())
                box.append(line)
                for perm in prov.get_permissions():
                    line.append(self.ui.create('checkbox', id=perm[0], text=perm[1], \
                        value=(perm[0] in item.permissions)))
        self.find('users').post_item_bind = post_user_bind

        def post_user_update(object, collection, item, ui):
            box = ui.find('permissions')
            for prov in PermissionProvider.get_all():
                for perm in prov.get_permissions():
                    has = box.find(perm[0]).value
                    if has and not perm[0] in item.permissions:
                        item.permissions.append(perm[0])
                    if not has and perm[0] in item.permissions:
                        item.permissions.remove(perm[0])
        self.find('users').post_item_update = post_user_update

        self.refresh()

    def refresh(self):
        self.binder.autodiscover().populate()

    @on('save-button', 'click')
    @restrict('configurator:configure')
    def save(self):
        self.binder.update()
        for user in ajenti.config.tree.users.values():
            if not '|' in user.password:
                user.password = UserManager.get().hash_password(user.password)
        self.binder.populate()
        ajenti.config.save()
        self.context.notify('info', 'Saved')

    @on('fake-ssl', 'click')
    def on_gen_ssl(self):
        host = self.find('fake-ssl-host').value
        path = self.find('fake-ssl-path').value
        if host == '':
            self.context.notify('error', 'Please supply hostname')
        elif not os.path.exists(path):
            self.context.notify('error', 'Please supply valid path')
        else:
            self.gen_ssl(host, path.rstrip('/'))

    @intent('setup-fake-ssl')
    def gen_ssl(self, host, path):
        self.save()
        ajenti.config.tree.ssl.enable = True
        ajenti.config.tree.ssl.certificate_path = '%s/ajenti.crt' % path
        ajenti.config.tree.ssl.key_path = '%s/ajenti.key' % path
        ajenti.config.save()
        self.refresh()

        script = """
            echo '\n-> Generating key\n';
            openssl genrsa -des3 -out /tmp/ajenti.key -passout pass:1234 2048;
            echo '\n-> Generating certificate request\n';
            openssl req -new -key /tmp/ajenti.key -out /tmp/ajenti.csr -passin pass:1234 -subj /C=US/ST=NA/L=Nowhere/O=Acme\\ Inc/OU=IT/CN={0}/;
            echo '\n-> Removing passphrase\n';
            cp /tmp/ajenti.key /tmp/ajenti.key.org;
            openssl rsa -in /tmp/ajenti.key.org -out /tmp/ajenti.key -passin pass:1234;
            echo '\n-> Generating certificate\n';
            openssl x509 -req -days 365 -in /tmp/ajenti.csr -signkey /tmp/ajenti.key -out /tmp/ajenti.crt -passin pass:1234;
            cat /tmp/ajenti.key /tmp/ajenti.crt > {1}/ajenti.pem;
            rm /tmp/ajenti.*;
            echo '\n\n===================\nRestart Ajenti to apply changes!\n===================';
        """.format(host, path)
        self.context.launch('terminal', command=script)


@plugin
class ConfigurationPermissionsProvider (PermissionProvider):
    def get_name(self):
        return 'Configuration'

    def get_permissions(self):
        return [('configurator:configure', 'Change configuration')]
