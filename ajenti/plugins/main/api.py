from ajenti.api import *
from ajenti.ui import *


@p('title')
@interface
class SectionPlugin (UIElement):
	typeid = 'main:section'