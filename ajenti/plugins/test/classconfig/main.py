from ajenti.api import *
from ajenti.api.http import *
from ajenti.plugins.configurator.api import ClassConfigEditor
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on


@plugin
class SimpleConfigEditor (ClassConfigEditor):
    title = 'Simple demo config'
    icon = 'question'

    def init(self):
        self.append(self.ui.inflate('test:classconfig-simple-editor'))


@plugin
class SimpleClassconfigSection (SectionPlugin):
    default_classconfig = {'option1': 'qwerty', 'option2': 1}
    classconfig_editor = SimpleConfigEditor

    def init(self):
        self.title = 'Classconfig (simple)'
        self.icon = 'question'
        self.category = 'Demo'
        self.append(self.ui.inflate('test:classconfig-main'))

    def on_page_load(self):
        self.find('value').text = repr(self.classconfig)

    @on('config', 'click')
    def on_config_btn(self):
        self.context.launch('configure-plugin', plugin=self)
