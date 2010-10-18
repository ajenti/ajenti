import re

from ajenti.ui import UI
from ajenti.com import *
from ajenti import version
from ajenti.app.api import ICategoryProvider, IContentProvider
from ajenti.ui.template import BasicTemplate
from ajenti.app.helpers import EventProcessor, SessionPlugin, event
from ajenti.app.urlhandler import URLHandler, url, get_environment_vars
from api import IProgressBoxProvider


class RootDispatcher(URLHandler, SessionPlugin, EventProcessor, Plugin):
    categories = Interface(ICategoryProvider)
    # Plugin folders. This dict is until we make MUI support
    folders = {
        'top': '',
        'system': 'System',
        'hardware': 'Hardware',
        'apps': 'Applications',
        'servers': 'Servers',
        'tools': 'Tools',
        'other': 'Other',
        'bottom': ''
    }
    # Folder order
    folder_ids = ['top', 'system', 'apps', 'hardware', 'tools', 'servers', 'other', 'bottom']

    def on_session_start(self):
        self._cat_selected = 'Dashboard'
        self._about_visible = False
        
    def main_ui(self):
        templ = self.app.get_template('main.xml')
        templ.appendChildInto('main-content', self.selected_category.get_ui())
        if self._about_visible:
            templ.appendChildInto('main-content', self.get_ui_about())
        for p in self.app.grab_plugins(IProgressBoxProvider):
            if p.has_progress():
                templ.appendChildInto(
                    'progressbox-placeholder', 
                    UI.TopProgressBox(
                        text=p.get_progress(),
                        icon=p.icon,
                        title=p.title,
                        can_abort=p.can_abort
                    )
                )
                break
        return templ

    def do_init(self):
        cat = None
        for c in self.categories:
            if c.get_name() == self._cat_selected: # initialize current plugin
                cat = c
        self.selected_category = cat
        if cat.disabled:
            raise cat.disabled
        cat.on_init()

    def get_ui_about(self):
        ui = UI.Centerer(
                UI.VContainer(
                    UI.Image(file='/dl/core/ui/logo_big.png'),
                    UI.Spacer(height=6),
                    UI.Label(text='Ajenti '+version, size=4),
                    UI.Label(text='Your personal server affairs agent'),
                    UI.Spacer(height=10),
                    UI.HContainer(
                        UI.OutLinkLabel(url='http://www.assembla.com/spaces/ajenti/wiki?id=aLa8XiGfWr36nLeJe5cbLA', text='Wiki'),
                        UI.OutLinkLabel(url='http://www.assembla.com/spaces/ajenti/wiki?id=ajenti&wiki_id=Developers', text='Credits'),
                        UI.OutLinkLabel(text='License', url='http://www.gnu.org/licenses/lgpl.html'),
                        UI.OutLinkLabel(text='Bugs', url='http://www.assembla.com/spaces/ajenti/support/tickets'),
                        spacing=6
                    ),
                    UI.Spacer(height=10),
                    UI.Button(text='Close', id='closeabout')
                )
            )
        return UI.DialogBox(ui, hideok=True, hidecancel=True)

    @url('^/$')
    def process(self, req, start_response):
        self.do_init()

        templ = self.app.get_template('index.xml')

        cat = None
        v = UI.VContainer(spacing=0)

        # Sort plugins by name
        cats = self.categories
        cats = sorted(cats, key=lambda p: p.text)

        for fld in self.folder_ids:
            cat_vc = UI.VContainer(spacing=0)
            if self.folders[fld] == '':
                cat_folder = cat_vc # Omit wrapper for special folders
            else:
                cat_folder = UI.CategoryFolder(
                                cat_vc,
                                text=self.folders[fld],
                                icon='/dl/core/ui/catfolders/'+ fld + '.png'
                                    if self.folders[fld] != '' else '',
                                id=fld
                             )
            # cat_vc will be VContainer or CategoryFolder

            exp = False
            empty = True
            for c in cats:
                enabled = c.disabled is None
                        
                if (c.folder == fld and enabled) \
                    or (fld == 'other' and not enabled): # Put corresponding plugins in this folder
                    empty = False
                    if c == self.selected_category:
                        cat_vc.append(UI.Category(icon=c.icon, name=c.text, id=c.get_name(), selected='true'))
                        exp = True
                    else:
                        cat_vc.append(UI.Category(icon=c.icon, name=c.text, id=c.get_name()))

            if not empty: v.append(cat_folder)
            cat_folder['expanded'] = exp

        templ.appendChildInto('leftplaceholder', v)
        templ.appendChildInto('rightplaceholder', self.main_ui().elements())
        templ.appendChildInto('version', UI.Label(text='Ajenti '+version, size=2))
        templ.appendChildInto('links',
            UI.HContainer(
                UI.LinkLabel(text='About', id='about'),
                UI.OutLinkLabel(text='License', url='http://www.gnu.org/licenses/lgpl.html')
            ))
            
        return templ.render()

    @url('^/session_reset$')
    def process_reset(self, req, start_response):
        self.app.session.clear()
        start_response('301 Moved Permanently', [('Location', '/')])
        return ''

    @event('category/click')
    def handle_category(self, event, params, **kw):
        if not isinstance(params, list):
            return
        if len(params) != 1:
            return

        self._cat_selected = params[0]
        self.do_init()

    @event('linklabel/click')
    def handle_linklabel(self, event, params, vars=None):
        if params[0] == 'about':
            self._about_visible = True

    @event('button/click')
    def handle_abort(self, event, params, **kw):
        if params[0] == 'aborttask':
            for p in self.app.grab_plugins(IProgressBoxProvider):
                if p.has_progress():
                    p.abort()
        if params[0] == 'closeabout':
            self._about_visible = False

    @url('^/handle/.+')
    def handle_generic(self, req, start_response):
        # Iterate through the IEventDispatchers and find someone who will take care of the event
        # TODO: use regexp for shorter event names, ex. 'btn_clickme/click'
        path = req['PATH_INFO'].split('/')
        event = '/'.join(path[2:4])
        params = path[4:]

        self.do_init()

        # Current module
        cat = filter(lambda x: x.get_name() == self._cat_selected, self.categories)[0]

        # Search self and current category for event handler
        for handler in (cat, self):
            if handler.match_event(event):
                vars = get_environment_vars(req)
                result = handler.event(event, params, vars = vars)
                if isinstance(result, str):
                    # For AJAX calls that do not require information
                    # just return ''
                    return result
                if isinstance(result, BasicTemplate):
                    # Useful for inplace AJAX calls (that returns partial page)
                    return result.render()

        # We have no result or handler - return default page
        main = self.main_ui()

        return main.render()

