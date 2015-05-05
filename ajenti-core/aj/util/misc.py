import subprocess
import traceback

import aj

# TODO sort this out


def platform_select(**values):
    """
    Selects a value from **kwargs** depending on runtime platform

    ::

        service = platform_select(
            debian='samba',
            ubuntu='smbd',
            centos='smbd',
            default='samba',
        )

    """
    if aj.platform_unmapped in values:
        return values[aj.platform_unmapped]
    if aj.platform in values:
        return values[aj.platform]
    return values.get('default', None)


def make_report(e):
    """
    Formats a bug report.
    """
    import platform as _platform
    from aj import platform, platform_unmapped, platform_string, version, debug

    tb = traceback.format_exc(e)
    tb = '\n'.join('    ' + x for x in tb.splitlines())


    import gevent
    import greenlet
    import psutil
    from aj.plugins import PluginManager

    return """Ajenti bug report
--------------------


Info | Value
----- | -----
Ajenti | %s
Platform | %s / %s / %s
Architecture | %s
Python | %s
Debug | %s
Loaded plugins | %s

Library | Version
------- | -------
gevent | %s
greenlet | %s
psutil | %s


%s

            """ % (
            version,
            platform, platform_unmapped, platform_string,
            subprocess.check_output(['uname', '-mp']).strip(),
            '.'.join([str(x) for x in _platform.python_version_tuple()]),
            debug,
            ', '.join(sorted(PluginManager.get(aj.context).get_loaded_plugins_list())),

            gevent.__version__,
            greenlet.__version__,
            psutil.__version__,

            tb,
        )
