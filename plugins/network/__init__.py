# pyflakes: disable-all
from .api import *
from .managers.centos_manager import *
from .managers.debian_manager import *
from .managers.gentoo_manager import *
from .managers.ubuntu_manager import *

def init(plugin_manager):
    import aj
    api.NetworkManager.any(aj.context)

    from .aug import ResolvConfEndpoint # skipcq: PYL-W0611
    from .main import ItemProvider # skipcq: PYL-W0611
    from .views import Handler # skipcq: PYL-W0611
