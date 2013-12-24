from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on


@plugin
class EventsDemo (SectionPlugin):
    def init(self):
        self.title = 'Event handlers'
        self.icon = 'question'
        self.category = 'Demo'

        self.append(self.ui.inflate('test:events-main'))

        def on_click(*args):
            self.context.notify('info', 'Directly attached event fired with arguments %s!' % repr(args))

        self.find('btn').on('click', on_click, 123, 456)
            

    @on('btn', 'click')
    def on_button_click(self):
        self.context.notify('info', 'Decorator-attached event fired!')
