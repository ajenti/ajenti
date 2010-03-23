from ajenti.com import Interface

class IRequestDispatcher(Interface):
    def match(self, uri):
        pass

    def process(self, req, start_response):
        pass


class IContentProvider(Interface):
    def content_path(self):
        pass


class ICategoryProvider(Interface):
    """ ICategoryProvider should contain:
    'category' property
    'get_ui()' method to retrieve main panel
    """
    category = {'text': 'Caption text',
                'description': 'Topic description',
                'icon': '/dl/core/ui/category-icon.png'}

    def get_ui():
        pass

class IEventDispatcher(Interface):
    def match_event(self, event):
        pass

    def event(self, event, *params, **kwparams):
        pass

