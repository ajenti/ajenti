from ajenti.com import Interface


class IXSLTFunctionProvider(Interface):
    def get_funcs(self):
        pass
        
        
class IXSLTTagProvider(Interface):
    def get_tags(self):
        pass                
