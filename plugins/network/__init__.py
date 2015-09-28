# pyflakes: disable-all
from .api import *
from .managers.centos_manager import *
from .managers.debian_manager import *
from .managers.gentoo_manager import *


def init(plugin_manager):
    import aj
    api.NetworkManager.any(aj.context)

    from .aug import ResolvConfEndpoint
    from .main import ItemProvider
    from .views import Handler
