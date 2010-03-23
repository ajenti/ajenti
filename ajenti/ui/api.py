from ajenti.com import Interface

class ITemplateProvider(Interface):
    def template(self):
        """ Returns dict of parameters
        {
         'path': []
         'include': []
        }
        """
        pass
