import os.path

from ajenti.com import *
from ajenti.app.api import IContentProvider

class ModuleContent(Plugin):
    abstract = True
    implements(IContentProvider)

    path = ''
    module = ''

    def content_path(self):
        if self.path == '' or self.module == '':
            raise AttributeError('You should provide path/module information')  
        norm_path = os.path.join(os.path.dirname(self.path),'files')
        return (self.module, norm_path)

