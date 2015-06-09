import main
import views


def init(plugin_manager):
    if 'dashboard' in plugin_manager and plugin_manager['dashboard']['imported']:
        import widget
