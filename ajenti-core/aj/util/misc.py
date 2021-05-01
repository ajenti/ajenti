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

    tb = traceback.format_exc()
    tb = '\n'.join('    ' + x for x in tb.splitlines())


    import gevent
    import greenlet
    import psutil
    from aj.plugins import PluginManager

    architecture = subprocess.check_output(['uname', '-m']).strip().decode()
    python = '.'.join(str(x) for x in _platform.python_version_tuple())
    plugins = ', '.join(sorted(PluginManager.get(aj.context).get_loaded_plugins_list())) if aj.context else 'None'

    return f"""Ajenti bug report
--------------------


Info | Value
----- | -----
Ajenti | {version}
Platform | {platform} / {platform_unmapped} / {platform_string}
Architecture | {architecture}
Python | {python}
Debug | {debug}
Loaded plugins | {plugins}

Library | Version
------- | -------
gevent | {gevent.__version__}
greenlet | {gevent.__version__}
psutil | {psutil.__version__}


{tb}

            """
