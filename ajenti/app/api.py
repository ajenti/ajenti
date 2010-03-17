from ajenti.com import Interface

class IRequestDispatcher(Interface):
    def match(self, uri):
        pass

    def process(self, req, start_response):
        pass


class IContentProvider(Interface):
    def content_path(self):
        pass


class IDOMCategoryProvider(Interface):
    def category_dom(self):
        pass
