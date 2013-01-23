from ajenti.api import plugin
from ajenti.plugins.dashboard.api import ConfigurableWidget


@plugin
class MuninWidget (ConfigurableWidget):
    name = 'Munin'
    icon = 'stethoscope'
    hidden = True

    def on_prepare(self):
        self.append(self.ui.inflate('munin:widget'))

    def on_start(self):
        self.find('plot').url = self.config['url']
        if 'period' in self.config:
            self.find('plot').period = self.config['period']

    def create_config(self):
        return {'url': '', 'period': ''}
