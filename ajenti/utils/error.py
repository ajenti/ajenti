from ajenti.utils import *
from ajenti import version
from ajenti.ui import UI
from ajenti.ui.template import BasicTemplate

import platform
import traceback



class BackendRequirementError(Exception):
    def __init__(self, interface):
        self.interface = interface

    def __str__(self):
        return 'Backend required: ' + str(self.interface)

class ConfigurationError(Exception):
    def __init__(self, hint):
        self.hint = hint

    def __str__(self):
        return 'Plugin failed to configure: ' + self.hint



def format_exception(app, err):
    print '\n%s\n' % err
    templ = app.get_template('error.xml')
    templ.appendChildInto('trace',
            UI.TextInputArea(value=err, width=350))
    templ.appendChildInto('report',
            UI.TextInputArea(value=make_report(app, err), width=350))
    return templ.render()

def format_error(app, ex):
    templ = app.get_template('disabled.xml')
    tool = None
    if isinstance(ex, BackendRequirementError):
        reason = 'Required backend is unavailable.'
        hint = 'You need a plugin that provides <b>%s</b> interface support for <b>%s</b> platform.<br/>' % (ex.interface, app.platform)
    elif isinstance(ex, ConfigurationError):
        reason = 'The plugin was unable to start with current configuration.<br/>Consider using configuration dialog for this plugin.'
        hint = ex.hint
    else:
        return format_exception(app, traceback.format_exc())

    templ.appendChildInto('reason', UI.CustomHTML(html=reason))
    templ.appendChildInto('hint', UI.CustomHTML(html=hint))
    return templ.render()

def make_report(app, err):
    from ajenti.plugmgr import PluginLoader
    pr = ''
    for p in sorted(PluginLoader.list_plugins().keys()):
        pr += p + '\n'

    return (('Ajenti %s bug report\n' +
           '--------------------\n\n' +
           'System: %s\n' +
           'Detected platform: %s\n' +
           'Detected distro: %s\n' +
           'Python: %s\n\n' +
           'Config path: %s\n\n' +
           '%s\n\n'
           'Loaded plugins:\n%s\n\n' +
           'Startup log:\n%s\n'
           )
            % (version(),
               shell('uname -a'),
               detect_platform(),
               detect_distro(),
               '.'.join([str(x) for x in platform.python_version_tuple()]),
               app.config.filename,
               err,
               pr,
               app.log.blackbox.buffer,
              ))
