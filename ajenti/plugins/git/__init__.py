
import ajenti
from ajenti.api import *
from ajenti.plugins import *

info = PluginInfo(
    title = 'GIT',
    icon = 'folder-close',
    description='Git Management Tool with Gitolite3 Authorization',
    dependencies =
    [
        PluginDependency('main'),
        PluginDependency('services'),
        BinaryDependency('git'),
        BinaryDependency('gitolite')
    ]
)

def init():
    import main;