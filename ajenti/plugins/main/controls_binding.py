from ajenti.api import *
from ajenti.ui import p, UIElement


@plugin
class BindTemplate (UIElement):
    typeid = 'bind:template'

    def init(self):
        self.visible = False
