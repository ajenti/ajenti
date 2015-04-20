import api
import managers.centos_manager
import managers.debian_manager


def init(plugin_manager):
    import aj
    api.TZManager.any(aj.context)

    import main
    import views


