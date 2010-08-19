from ajenti.app.helpers import ModuleContent


class CoreContentProvider(ModuleContent):
    path = __file__
    module = 'core'
    widget_files = ['widgets.xml']
    css_files = ['ui.css']
    js_files = ['ajax.js', 'ui.js', 'base64.js']
