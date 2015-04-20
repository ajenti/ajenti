import api
import managers.systemd_manager

try:
    import managers.upstart_manager
except ImportError:
    pass

import managers.sysv_manager
import main
import views

def init(plugin_manager):
    if 'dashboard' in plugin_manager and plugin_manager['dashboard']['imported']:
        import widget
