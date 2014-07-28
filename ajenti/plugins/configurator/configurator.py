from copy import deepcopy
import logging
import subprocess

import ajenti
import ajenti.locales
from ajenti.api import *
from ajenti.licensing import Licensing
from ajenti.plugins import manager
from ajenti.plugins.main.api import SectionPlugin, intent
from ajenti.ui import on
from ajenti.ui.binder import Binder, DictAutoBinding
from ajenti.users import UserManager, PermissionProvider, restrict
from ajenti.usersync import UserSyncProvider

from reconfigure.items.ajenti import UserData

from licensing import LicensingUI


@plugin
class ClassConfigManager (BasePlugin):
    def init(self):
        self.classes = []

    def reload(self):
        if self.context.user.name == 'root':
            self.classes = BasePlugin.get_instances(self.context)
            self.classes += BasePlugin.get_instances(self.context.parent)
        else:
            self.classes = filter(
                lambda x: not x.classconfig_root,
                BasePlugin.get_instances()
            )
        self.classes = filter(lambda x: x.classconfig_editor, self.classes)
        self.classes = list(set(self.classes))
        self.classes = sorted(
            self.classes,
            key=lambda x: x.classconfig_editor.title
        )


@plugin
class Configurator (SectionPlugin):
    def init(self):
        self.title = _('Configure')
        self.icon = 'wrench'
        self.category = ''
        self.order = 50

        self.append(self.ui.inflate('configurator:main'))

        self.binder = Binder(ajenti.config.tree, self.find('ajenti-config'))

        self.ccmgr = ClassConfigManager.get()
        if Licensing.licensing_active:
            self.find('licensing').append(LicensingUI.new(self.ui))
        else:
            self.find('licensing').delete()
        self.classconfig_binding = Binder(
            self.ccmgr,
            self.find('classconfigs')
        )

        def post_classconfig_bind(object, collection, item, ui):
            def configure():
                self.configure_plugin(item, notify=False)

            ui.find('configure').on('click', configure)

        self.find('classconfigs').find('classes') \
            .post_item_bind = post_classconfig_bind

        self.find('users').new_item = lambda c: UserData()

        def post_user_bind(object, collection, item, ui):
            provider = UserManager.get().get_sync_provider()
            editable = item.name != 'root'
            renameable = editable and provider.allows_renaming
            deletable = renameable

            ui.find('name-edit').visible = renameable
            ui.find('name-label').visible = not renameable
            ui.find('delete').visible = deletable

            box = ui.find('permissions')
            box.empty()

            p = PermissionProvider.get_all()
            for prov in p:
                line = self.ui.create('tab', title=prov.get_name())
                box.append(line)
                for perm in prov.get_permissions():
                    line.append(
                        self.ui.create(
                            'checkbox', id=perm[0],
                            text=perm[1], value=(perm[0] in item.permissions)
                        )
                    )

            def copy():
                self.save()
                newuser = deepcopy(item)
                newuser.name += '_'
                collection[newuser.name] = newuser
                self.refresh()

            ui.find('copy').on('click', copy)

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

    def on_page_load(self):
        self.refresh()

    @on('sync-users-button', 'click')
    def on_sync_users(self):
        self.save()
        prov = UserManager.get().get_sync_provider()
        try:
            prov.test()
            prov.sync()
        except Exception as e:
            self.context.notify('error', str(e))
        self.refresh()

    @on('configure-sync-button', 'click')
    def on_configure_sync(self):
        self.save()
        if UserManager.get().get_sync_provider().classconfig_editor is not None:
            self.configure_plugin(
                UserManager.get().get_sync_provider(),
                notify=False
            )
        self.refresh()

    def refresh(self):
        self.binder.unpopulate()

        self.find('sync-providers').labels = [
            x.title for x in UserSyncProvider.get_classes()
        ]
        self.find('sync-providers').values = [
            x.id for x in UserSyncProvider.get_classes()
        ]

        provider = UserManager.get().get_sync_provider()
        self.find('sync-providers').value = provider.id
        self.find('users-dt').addrow = _('Add') if provider.id == '' else None
        self.find('sync-users-button').visible = provider.id != ''
        self.find('password').visible = provider.id == ''
        self.find('configure-sync-button').visible = \
            provider.classconfig_editor is not None

        try:
            provider.test()
            sync_ok = True
        except Exception as e:
            self.context.notify('error', str(e))
            sync_ok = False

        self.find('sync-status-ok').visible = sync_ok
        self.find('sync-status-fail').visible = not sync_ok

        languages = sorted(ajenti.locales.list_locales())
        self.find('language').labels = [_('Auto'), 'en_US'] + languages
        self.find('language').values = ['', 'en_US'] + languages

        self.binder.setup().populate()
        self.ccmgr.reload()
        self.classconfig_binding.setup().populate()

    @on('save-button', 'click')
    @restrict('configurator:configure')
    def save(self):
        self.binder.update()

        UserManager.get().set_sync_provider(
            self.find('sync-providers').value
        )

        UserManager.get().hash_passwords()
        
        self.refresh()
        ajenti.config.save()
        self.context.notify(
            'info',
            _('Saved. Please restart Ajenti for changes to take effect.')
        )

    @on('fake-ssl', 'click')
    def on_gen_ssl(self):
        host = self.find('fake-ssl-host').value
        if host == '':
            self.context.notify('error', _('Please supply hostname'))
        else:
            self.gen_ssl(host)

    @on('restart-button', 'click')
    def on_restart(self):
        ajenti.restart()

    @intent('configure-plugin')
    def configure_plugin(self, plugin=None, notify=True):
        self.find('tabs').active = 1
        self.refresh()

        if plugin and notify:
            self.context.notify(
                'info',
                _('Please configure %s plugin!') %
                plugin.classconfig_editor.title
            )

        self.activate()

        dialog = self.find('classconfigs').find('dialog')
        dialog.find('container').empty()
        dialog.visible = True

        editor = plugin.classconfig_editor.new(self.ui)
        dialog.find('container').append(editor)

        if editor.find('bind'):
            logging.warn('%s uses old dictbinding classconfig editor layout')
            binder = DictAutoBinding(plugin, 'classconfig', editor.find('bind'))
        else:
            binder = Binder(plugin, editor)
        binder.populate()

        def save(button=None):
            dialog.visible = False
            binder.update()
            plugin.save_classconfig()
            self.save()

        dialog.on('button', save)

    @intent('setup-fake-ssl')
    def gen_ssl(self, host):
        self.save()
        subprocess.call(['ajenti-ssl-gen', host, '-f'])
        ajenti.config.load()
        self.refresh()


@plugin
class ConfigurationPermissionsProvider (PermissionProvider):
    def get_name(self):
        return _('Configuration')

    def get_permissions(self):
        return [
            ('configurator:configure', _('Modify Ajenti configuration')),
            ('configurator:restart', _('Restart Ajenti')),
        ]
