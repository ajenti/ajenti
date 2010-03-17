import re

import ajenti.ui as ui
from ajenti.com import *
from ajenti.app.api import IRequestDispatcher, IDOMCategoryProvider

class RootDispatcher(Plugin):
    implements(IRequestDispatcher)
    
    categories = Interface(IDOMCategoryProvider)

    def match(self, uri):
        if re.match('^/$', uri):
            return True
        else:
            return False

    def process(self, req, start_response):
        mw = ui.MainWindow()

        v = ui.VContainer() 
        cat_doms = [cat.category_dom() for cat in self.categories]
        for c in cat_doms:
            v.appendChild(c)

        mw.top(ui.TopBar())
        mw.left(v)

        d = ui.Document([mw])

        return d.toprettyxml('')
            
            
