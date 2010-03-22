import re

import ajenti.ui as ui
from ajenti.com import *
from ajenti.app.api import IRequestDispatcher, ICategoryProvider

class TestCategory(Plugin):
    implements(ICategoryProvider)

    def category_dom(self):
        return { 'text': 'Caption',
                 'description': 'Description',
                 'img': '/dev/null' }

class RootDispatcher(Plugin):
    implements(IRequestDispatcher)
    
    categories = Interface(ICategoryProvider)

    def match(self, uri):
        if re.match('^/$', uri):
            return True
        else:
            return False

    def process(self, req, start_response):
        templ = self.app.get_template('index.xml')
        h = ui.Html()

        v = ui.VContainer()
        for c in self.categories:
            v.vnode(ui.Category(c.category_dom()))

        templ.appendChildInto('leftplaceholder', v)

        number = req['app.session'].get('number', None)
        if not number:
            import random
            number = str(random.randint(1, 9000*9000))
            req['app.session']['number'] = number
        templ.appendChildInto('topplaceholder', h.p({'py:content':number}))

        # Debug, to see how template looks before template engine
        print templ.toxml()

        return templ.render()
            
            
