from ajenti.utils import *
from ajenti import version
from ajenti.ui import UI
from ajenti.ui.template import BasicTemplate
import platform

def format_error(app, err):
    templ = app.get_template('error.xml')
    err = err.replace('\n', '[br]')
    templ.appendChildInto('trace',
            UI.TextInputArea(text=err, width=350))
    templ.appendChildInto('report',
            UI.TextInputArea(text=make_report(app, err), width=350))
    return templ.render()

def make_report(app, err):
    return (('Ajenti %s bug report\n' +
           '--------------------\n\n' +
           'System: %s\n' +
           'Detected platform: %s\n' +
           'Detected distro: %s\n' +
           'Python: %s\n\n' +
           'Loaded plugins:\n%s\n\n' +
           '%s')
            % (version,
               shell('uname -a'),
               detect_platform(),
               detect_distro(),
               '.'.join(platform.python_version_tuple()),
               str(app.class_list()).replace(',','\n'),
               err
              )).replace('\n', '[br]')
