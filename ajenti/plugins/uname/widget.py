import subprocess
from ajenti.api import plugin
from ajenti.plugins.dashboard.api import DashboardWidget
from ajenti.plugins.dashboard.api import ConfigurableWidget

@plugin
class UnameWidget(DashboardWidget):
    name = _('Uname')
    icon = 'cog'

    def init(self):
        self.append(self.ui.inflate('uname:uname'))
        self.find('icon').text = 'cog'
        self.find('name').text = 'Uname:'
        self.find('value').text = subprocess.check_output(['uname', '-srm'])


@plugin

class MyUnameWidget(ConfigurableWidget):
    name = _('Uname (configurable)')
    icon = 'cog'
    options = 'asnrvmpio'

    def on_prepare(self):
        self.append(self.ui.inflate('uname:cfguname'))

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
        options={}
        for o in self.options:
            if o in 'srm':
                options['opt_%s'%o]=True
            else:
                options['opt_%s'%o]=False
        return options

    def on_config_start(self):
        for o in self.options:
            opt = 'opt_%s' % o
            if self.config[opt]:
                self.dialog.find(opt).value = True

    def on_config_save(self):
        for o in self.options:
            opt = 'opt_%s' % o
            self.config[opt] = self.dialog.find(opt).value
