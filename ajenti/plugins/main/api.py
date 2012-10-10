from ajenti.api import *
from ajenti.ui import *


@p('title')
@p('order', default=99)
@p('category', default='Other')
@p('active', default=False)
@interface
class SectionPlugin (BasePlugin, UIElement):
    typeid = 'main:section'
