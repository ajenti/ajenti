from ajenti.app.helpers import ModuleContent

class CoreContentProvider(ModuleContent):
    path = __file__
    module = 'core' 
    widget_files = ['widgets.xml']

