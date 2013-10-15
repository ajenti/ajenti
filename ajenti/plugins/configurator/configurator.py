import subprocess

import ajenti
import ajenti.locales
from ajenti.api import *
from ajenti.plugins import manager
from ajenti.plugins.main.api import SectionPlugin, intent
from ajenti.ui import on
from ajenti.ui.binder import Binder, DictAutoBinding
from ajenti.users import UserManager, PermissionProvider, restrict
from ajenti.usersync import UserSyncProvider
from reconfigure.items.ajenti import UserData


@plugin
class ClassConfigManager (BasePlugin):
    def init(self):
        self.classes = []

    def reload(self):
        if self.context.user.name == 'root':
            self.classes = BasePlugin.get_instances(self.context)
            self.classes += BasePlugin.get_instances(self.context.parent)
        else:
            self.classes = filter(lambda x: not x.classconfig_root, BasePlugin.get_instances())
        self.classes = filter(lambda x: x.classconfig_editor, self.classes)
        self.classes = list(set(self.classes))


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
        self.classconfig_binding = Binder(self.ccmgr, self.find('classconfigs'))

        def post_classconfig_bind(object, collection, item, ui):
            def configure():
                self.configure_plugin(item, notify=False)

            ui.find('configure').on('click', configure)

        self.find('classconfigs').find('classes').post_item_bind = post_classconfig_bind

        self.find('users').new_item = lambda c: UserData()

        def post_user_bind(object, collection, item, ui):
            box = ui.find('permissions')
            box.empty()
            ui.find('name-edit').visible = item.name != 'root'
            ui.find('name-label').visible = item.name == 'root'
            for prov in PermissionProvider.get_all():
                line = self.ui.create('tab', title=prov.get_name())
                box.append(line)
                for perm in prov.get_permissions():
                    line.append(
                        self.ui.create('checkbox', id=perm[0], text=perm[1], value=(perm[0] in item.permissions))
                    )
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
            if ui.find('password').value:
                item.password = ui.find('password').value
        self.find('users').post_item_update = post_user_update

    def on_page_load(self):
        self.refresh()

    @on('sync-users-button', 'click')
    def on_sync_users(self):
        self.save()
        UserManager.get(manager.context).get_sync_provider().sync()
        self.refresh()

    @on('configure-sync-button', 'click')
    def on_configure_sync(self):
        self.save()
        self.configure_plugin(UserManager.get(manager.context).get_sync_provider(), notify=False)
        self.refresh()

    def refresh(self):
        self.binder.reset()

        self.find('sync-providers').labels = [x.title for x in UserSyncProvider.get_classes()]
        self.find('sync-providers').values = [x.id    for x in UserSyncProvider.get_classes()]

        provider = UserManager.get(manager.context).get_sync_provider()
        self.find('sync-providers').value = provider.id
        self.find('add-user-button').visible = provider.id == ''
        self.find('sync-users-button').visible = provider.id != ''
        self.find('password').visible = provider.id == ''
        self.find('configure-sync-button').visible = provider.classconfig_editor is not None

        sync_ok = provider.test()
        self.find('sync-status-ok').visible = sync_ok
        self.find('sync-status-fail').visible = not sync_ok

        languages = sorted(ajenti.locales.list_locales())
        self.find('language').labels = [_('Auto')] + languages
        self.find('language').values = [''] + languages

        self.binder.autodiscover().populate()
        self.ccmgr.reload()
        self.classconfig_binding.reset().autodiscover().populate()

    @on('save-button', 'click')
    @restrict('configurator:configure')
    def save(self):
        self.binder.update()
        
        UserManager.get(manager.context).set_sync_provider(self.find('sync-providers').value)

        for user in ajenti.config.tree.users.values():
            if not '|' in user.password:
                user.password = UserManager.get(manager.context).hash_password(user.password)

        self.refresh()
        ajenti.config.save()
        self.context.notify('info', _('Saved. Please restart Ajenti for changes to take effect.'))

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
            self.context.notify('info', _('Please configure %s plugin!') % plugin.classconfig_editor.title)
        
        self.activate()

        dialog = self.find('classconfigs').find('dialog')
        dialog.find('container').empty()
        dialog.visible = True

        editor = plugin.classconfig_editor.new(self.ui)
        dialog.find('container').append(editor)
        binder = DictAutoBinding(plugin, 'classconfig', editor.find('bind'))
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
