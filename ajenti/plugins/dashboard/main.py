from ajenti.ui import *
from ajenti.com import *
from ajenti.app.api import ICategoryProvider

class Dashboard(Plugin):
    implements(ICategoryProvider)

    text = 'Dashboard'
    description = 'Server status'
    icon = '/dl/dashboard/icon.png'

    def category_dom(self):
        return { 'text':self.text, 
                 'description':self.description, 
                 'img':self.icon }

