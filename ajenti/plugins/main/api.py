from ajenti.api import *
from ajenti.ui import *


@p('title')
@p('order', default=99)
@p('category', default='Other')
@p('active', default=False)
@interface
class SectionPlugin (BasePlugin, UIElement):
    typeid = 'main:section'
    _intents = {}

    def init(self):
        for k, v in self.__class__.__dict__.iteritems():
            if hasattr(v, '_intent'):
                self._intents[v._intent] = getattr(self, k)

    def activate(self):
        self.context.endpoint.switch_tab(self)

    def on_page_load(self):
        pass


def intent(name):
    def decorator(fx):
        fx._intent = name
        return fx
    return decorator
