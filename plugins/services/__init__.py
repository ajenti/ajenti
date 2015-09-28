# pyflakes: disable-all
from .api import *
from .managers.systemd_manager import *

try:
    from .managers.upstart_manager import *
except ImportError:
    pass

from .managers.sysv_manager import *
from .main import *
from .views import *


def init(plugin_manager):
    if 'dashboard' in plugin_manager and plugin_manager['dashboard']['imported']:
        from .widget import ServiceWidget
