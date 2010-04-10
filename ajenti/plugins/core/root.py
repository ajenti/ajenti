import re

from ajenti.ui import UI
from ajenti.com import *

from ajenti.app.api import ICategoryProvider, IContentProvider
from ajenti.ui.template import BasicTemplate
from ajenti.app.helpers import EventProcessor, event
from ajenti.app.urlhandler import URLHandler, url, get_environment_vars

class RootDispatcher(URLHandler, EventProcessor, Plugin):

    categories = Interface(ICategoryProvider)

    def main_ui(self):
        templ = self.app.get_template('main.xml')

        cat_selected = self.app.session.get('cat_selected',0)

        cat = None
        v = UI.VContainer()
        for num, c in enumerate(self.categories):
            if num == cat_selected:
                v.vnode(UI.Category(c.category, id=str(num), selected='true'))
                cat = c
            else:
                v.vnode(UI.Category(c.category, id=str(num)))

        templ.appendChildInto('leftplaceholder', v)

        templ.appendChildInto('rightplaceholder', cat.get_ui())

        return templ

    def do_init(self):
        cat_selected = self.app.session.get('cat_selected',0)
        cat = None
        for num, c in enumerate(self.categories):
            if num == cat_selected:
                cat = c
        cat.on_init()

    @url('^/$')
    def process(self, req, start_response):
        templ = self.app.get_template('index.xml')

        self.do_init()
        main = self.main_ui()

        templ.appendChildInto('body', main.elements())

        return templ.render()

    @event('category/click')
    def handle_category(self, event, params, **kw):
        if not isinstance(params, list):
            return
        if len(params) != 1:
            return
        try:
            cat = int(params[0])
        except:
            return

        self.app.session['cat_selected'] = cat
        self.do_init()

    @url('^/handle/.+')
    def handle_generic(self, req, start_response):
        # Iterate through the IEventDispatchers and find someone who will take care of the event
        # TODO: use regexp for shorter event names, ex. 'btn_clickme/click'
        path = req['PATH_INFO'].split('/')
        event = '/'.join(path[2:4])
        params = path[4:]

        self.do_init()

        # Current module
        cat = self.app.session.get('cat_selected',0)

        # Search self and current category for event handler
        for handler in (self.categories[cat], self):
            if handler.match_event(event):
                vars = get_environment_vars(req)
                result = handler.event(event, params, vars = vars)
                if isinstance(result, str):
                    # For AJAX calls that do not require information
                    # just return ''
                    return result
                if isinstance(result, BasicTemplate):
                    # Usefull for inplace AJAX calls (that returns partial page)
                    return result.render()

        # We have no result or handler - return default page
        main = self.main_ui()

        return main.render()

