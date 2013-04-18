from ajenti.api import *
from ajenti.ui import *


@p('title')
@interface
class ClassConfigEditor (BasePlugin, UIElement):
    typeid = 'configurator:classconfig-editor'
