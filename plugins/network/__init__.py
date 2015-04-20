import api
import managers.centos_manager
import managers.debian_manager

def init(plugin_manager):
    import aj
    api.NetworkManager.any(aj.context)

    import aug
    import main
    import views


