# pyflakes: disable-all
from .api import *
from .managers.centos_manager import *
from .managers.debian_manager import *


def init(plugin_manager):
    import aj
    api.TZManager.any(aj.context)

    from .main import ItemProvider
    from .views import Handler
