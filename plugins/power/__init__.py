# pyflakes: disable-all
from .main import *
from .views import *


def init(plugin_manager):
    if 'dashboard' in plugin_manager and plugin_manager['dashboard']['imported']:
        from .widget import PowerWidget
