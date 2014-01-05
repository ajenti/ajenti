from ajenti.api import plugin
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on


@plugin
class NotificationsDemo (SectionPlugin):
    def init(self):
        self.title = 'Notifications'
        self.icon = 'question'
        self.category = 'Demo'

        self.append(self.ui.inflate('test:notifications-main'))

    @on('show', 'click')
    def on_show(self):
        self.context.notify(self.find('style').value, self.find('text').value)
