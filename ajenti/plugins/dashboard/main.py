from ajenti.com import *
from ajenti.ui import Category
from ajenti.app.api import IDOMCategoryProvider

class Dashboard(Plugin):
    implements(IDOMCategoryProvider)

    text = 'Dashboard'
    description = 'Server status'
    icon = 'dashboard/icon.png'

    def category_dom(self):
        return Category(text=self.text, 
                        description=self.description, 
                        icon=self.icon)

