import api
import managers.systemd_manager

try:
    import managers.upstart_manager
except ImportError:
    pass

import managers.sysv_manager
import main
import views
import widget
