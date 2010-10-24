from ajenti.com import Interface


class IRequestDispatcher(Interface):
    def match(self, uri):
        pass

    def process(self, req, start_response):
        pass


class ICategoryProvider(Interface):
    def get_ui():
        pass


class IModuleConfig(Interface):
    plugin = ''


class IEventDispatcher(Interface):
    def match_event(self, event):
        pass

    def event(self, event, *params, **kwparams):
        pass
        
class IXSLTFunctionProvider(Interface):
    def get_funcs(self):
        pass


