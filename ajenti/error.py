from ajenti.ui import UI
from ajenti.ui.template import BasicTemplate

def format_error(app, err):
    templ = app.get_template('error.xml')
    err = err.replace('\n', '[br]')
    templ.appendChildInto('trace', UI.TextInputArea(text=err, width=350))
    return templ.render()
    


