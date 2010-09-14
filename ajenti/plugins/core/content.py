from ajenti.app.helpers import ModuleContent


class CoreContentProvider(ModuleContent):
    path = __file__
    module = 'core'
    widget_files = [
        'generics.xslt', 
        'main.xslt', 
        'basic.xslt', 
        'inputs.xslt', 
        'complex.xslt', 
        'forms.xslt', 
        'tables.xslt'
       ]
    css_files = [
        'general.css', 
        'main.css', 
        'basic.css', 
        'complex.css',
        'forms.css',
        'tables.css'
       ]
    js_files = ['ajax.js', 'ui.js', 'base64.js']
