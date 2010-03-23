import platform

from ajenti.ui import *
from ajenti import version
from ajenti.utils import detect_distro
from ajenti.app.helpers import CategoryPlugin

class Dashboard(CategoryPlugin):

    text = 'Dashboard'
    description = 'Dashboard overview'
    icon = '/dl/dashboard/icon.png'

    def get_ui(self):
        h = HContainer(
                Image('/dl/dashboard/server.png'), 
                Spacer(10,1),
                VContainer(
                    Text(platform.node()),
                    Text('Ajenti ' + version),
                    Text(detect_distro())
                )
            )
        return h
