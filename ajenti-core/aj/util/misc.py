import logging
import subprocess
import traceback

#TODO sort this out


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
    import catcher
    import platform as _platform
    from aj import platform, platform_unmapped, platform_string, installation_uid, version, debug

    tb = traceback.format_exc(e)
    tb = '\n'.join('    ' + x for x in tb.splitlines())

    catcher_url = None
    try:
        report = catcher.collect(e)
        html = catcher.formatters.HTMLFormatter().format(report, maxdepth=3)
        catcher_url = catcher.uploaders.AjentiOrgUploader().upload(html)
    except:
        pass

    import gevent
    import greenlet
    import reconfigure
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
Installation | %s
Debug | %s
Catcher report | %s
Loaded plugins | %s

Library | Version
------- | -------
gevent | %s
greenlet | %s
reconfigure | %s
psutil | %s


%s

            """ % (
        version,
        platform, platform_unmapped, platform_string.strip(),
        subprocess.check_output(['uname', '-mp']).strip(),
        '.'.join([str(x) for x in _platform.python_version_tuple()]),
        installation_uid,
        debug,
        catcher_url or 'Failed to upload traceback',
        ', '.join(sorted(PluginManager.get(aj.context).get_order())),

        gevent.__version__,
        greenlet.__version__,
        reconfigure.__version__,
        psutil.__version__,

        tb,
    )
