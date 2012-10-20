from ajenti.api import *
from ajenti.ui import UIElement, p


@p('config', public=False)
@p('container', type=int, default=0)
@p('index', type=int, default=0)
@interface
class DashboardWidget (BasePlugin, UIElement):
    typeid = 'dashboard:widget'
    name = '---'
    icon = ''
