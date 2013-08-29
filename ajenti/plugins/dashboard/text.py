from ajenti.api import plugin
from ajenti.plugins.dashboard.api import ConfigurableWidget


@plugin
class TextWidget (ConfigurableWidget):
    name = _('Text')
    icon = 'font'

    def on_prepare(self):
        self.append(self.ui.inflate('dashboard:text'))

    def on_start(self):
        self.find('text').text = self.config['text']

    def create_config(self):
        return {'text': ''}

    def on_config_start(self):
        pass

    def on_config_save(self):
        self.config['text'] = self.dialog.find('text').value
