import subprocess

import ajenti
from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin, intent
from ajenti.ui import on
from ajenti.ui.binder import Binder, DictAutoBinding
from ajenti.users import UserManager, PermissionProvider, restrict
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
        self.classconfig_rows = {}

        def post_classconfig_bind(object, collection, item, ui):
            self.classconfig_rows[item] = ui
            editor = item.classconfig_editor.new(self.ui)
            ui.find('container').append(editor)
            binder = DictAutoBinding(item, 'classconfig', editor.find('bind'))
            binder.populate()

            def save():
                binder.update()
                item.save_classconfig()
                self.context.notify('info', _('Saved'))

            ui.find('save').on('click', save)

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

    def refresh(self):
        self.binder.reset().autodiscover().populate()
        self.ccmgr.reload()
        self.classconfig_binding.reset().autodiscover().populate()

    @on('save-button', 'click')
    @restrict('configurator:configure')
    def save(self):
        self.binder.update()
        for user in ajenti.config.tree.users.values():
            if not '|' in user.password:
                user.password = UserManager.get().hash_password(user.password)
        self.binder.populate()
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
    def configure_plugin(self, plugin=None):
        self.find('tabs').active = 1
        self.refresh()
        #if plugin in self.classconfig_rows:
        #    self.classconfig_rows[plugin].children[0].expanded = True
        #    print self.classconfig_rows[plugin].children[0]
        if plugin:
            self.context.notify('info', _('Please configure %s plugin!') % plugin.classconfig_editor.title)
        self.activate()

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
