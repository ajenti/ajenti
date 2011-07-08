from ajenti.api import *
from ajenti.ui import *


class TutorialPlugin(CategoryPlugin):
    text = 'Tutorial' # name for the left pane
    icon = '/dl/tutorial/icon.png'
    folder = 'apps'

    def get_ui(self):
        ui = self.app.inflate('tutorial:main')
        return ui
   
