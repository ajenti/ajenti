import subprocess

from ajenti.api import plugin
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.plugins.dashboard.api import ConfigurableWidget


@plugin
class MyUnameWidget(ConfigurableWidget):
    name = _('uname')
    icon = 'cog'
    options = 'asnrvmpio'

    def on_prepare(self):
        self.append(self.ui.inflate('uname:widget'))

    def on_start(self):
        args = ''
        if self.config['opt_a']:
            args += 'a'
        else:
            for o in self.options[1:]:
                if self.config['opt_%s' % o]:
                    args += o

        if len(args):
            args = '-' + args
        self.find('value').text = subprocess.check_output(['uname', args])

    def create_config(self):
        options = {}
        for o in self.options:
            options['opt_%s'%o] = o in 'srm'
        return options

    def on_config_start(self):
        for o in self.options:
            opt = 'opt_%s' % o
            self.dialog.find(opt).value = self.config[opt]

    def on_config_save(self):
        for o in self.options:
            opt = 'opt_%s' % o
            self.config[opt] = self.dialog.find(opt).value
