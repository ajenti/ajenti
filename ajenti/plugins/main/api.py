from ajenti.api import *
from ajenti.ui import *


@p('title')
@p('active', default=False)
@interface
class SectionPlugin (UIElement):
    typeid = 'main:section'
