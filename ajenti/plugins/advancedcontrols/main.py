from ajenti.app.helpers import ModuleContent


class AdvancedControlsContent(ModuleContent):
    path = __file__
    module = 'advancedcontrols'
    css_files = ['ui.css']
    js_files = ['ui.js']
    widget_files = ['widgets.xml']
