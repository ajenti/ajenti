import os.path

from ajenti.com import Plugin, implements
from ajenti.ui.api import ITemplateProvider
from ajenti.app.helpers import ModuleContent

class ContentProvider(ModuleContent):
    path = __file__
    module = 'core' 

class TemplateProvider(Plugin):
    implements(ITemplateProvider)

    includes = ['widgets.xml']

    def template(self):
        norm_path = os.path.join(os.path.dirname(__file__),'templates')
        return {'path':norm_path, 'include':self.includes}

