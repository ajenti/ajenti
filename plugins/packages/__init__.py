import api
import main
import views
import tasks

try:
    import managers.apt_manager
except ImportError:
    pass

try:
    import managers.yum_manager
except ImportError:
    pass
