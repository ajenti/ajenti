import os.path

from ajenti.com import Plugin, implements
from ajenti.app.helpers import ModuleContent
from ajenti.ui.api import ITemplateProvider

class ContentProvider(ModuleContent):
    path = __file__
    module = 'dashboard' 

class TemplateProvider(Plugin):
    implements(ITemplateProvider)

    includes = ['dashboard-widget.xml']

    def template(self):
        norm_path = os.path.join(os.path.dirname(__file__),'templates')
        return {'path':[norm_path], 'include':self.includes}

