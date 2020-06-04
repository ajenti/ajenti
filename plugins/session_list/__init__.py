from .main import ItemProvider
from .views import Handler

def init(plugin_manager):
    if 'dashboard' in plugin_manager and plugin_manager['dashboard']['imported']:
        from .widget import SessionWidget