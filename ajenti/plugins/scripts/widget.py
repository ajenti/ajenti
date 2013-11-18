import gevent
import subprocess

from ajenti.api import plugin
from ajenti.plugins.dashboard.api import ConfigurableWidget
from ajenti.users import PermissionProvider, restrict
from ajenti.ui import on


@plugin
class ScriptWidget (ConfigurableWidget):
    name = _('Script')
    icon = 'play'

    def on_prepare(self):
        self.append(self.ui.inflate('scripts:widget'))

    def on_start(self):
        self.command = self.config['command']
        if not self.command:
            return
        self.find('name').text = self.config['title']

    def create_config(self):
        return {'command': '', 'title': '', 'terminal': False}

    def on_config_start(self):
        self.dialog.find('command').value = self.config['command']
        self.dialog.find('title').value = self.config['title']
        self.dialog.find('terminal').value = self.config['terminal']

    @on('edit', 'click')
    def on_edit(self):
        self.begin_configuration()

    def on_config_save(self):
        self.config['command'] = self.dialog.find('command').value
        self.config['title'] = self.dialog.find('title').value
        self.config['terminal'] = self.dialog.find('terminal').value

    @on('start', 'click')
    @restrict('scripts:run')
    def on_s_start(self):
        if self.config['terminal']:
            self.context.launch('terminal', command=self.config['command'])
        else:
            p = subprocess.Popen(self.config['command'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.context.notify('info', _('Launched'))

            def worker():
                o, e = p.communicate()
                self.context.notify('info', o + e)

            gevent.spawn(worker)


@plugin
class ScriptPermissionsProvider (PermissionProvider):
    def get_name(self):
        return _('Scripts')

    def get_permissions(self):
        return [
            ('scripts:run', _('Run scripts')),
        ]
