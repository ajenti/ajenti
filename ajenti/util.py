from datetime import timedelta
import catcher
import locale
import logging
import subprocess
import sys
import time
import traceback

import ajenti


def public(f):
    """"
    Use a decorator to avoid retyping function/class names.

    Based on an idea by Duncan Booth:
    http://groups.google.com/group/comp.lang.python/msg/11cbb03e09611b8a

    Improved via a suggestion by Dave Angel:
    http://groups.google.com/group/comp.lang.python/msg/3d400fb22d8a42e1

    """
    all = sys.modules[f.__module__].__dict__.setdefault('__all__', [])
    if f.__name__ not in all:  # Prevent duplicates if run from an IDE.
        all.append(f.__name__)
    return f
public(public)  # Emulate decorating ourself


@public
def str_fsize(sz):
    """
    Formats file size as string (i.e., 1.2 Mb)
    """
    if sz < 1024:
        return '%.1f bytes' % sz
    sz /= 1024.0
    if sz < 1024:
        return '%.1f KB' % sz
    sz /= 1024.0
    if sz < 1024:
        return '%.1f MB' % sz
    sz /= 1024.0
    if sz < 1024:
        return '%.1f GB' % sz
    sz /= 1024.0
    return '%.1f TB' % sz


@public
def str_timedelta(s):
    """
    Formats a time delta (i.e., "5 days, 5:06:07")
    """
    return str(timedelta(0, s)).split('.')[0]


@public
def cache_value(duration=None):
    """
    Makes a function lazy.

    :param duration: cache duration in seconds (default: infinite)
    :type  duration: int
    """
    def decorator(fx):
        fx.__cached = None
        fx.__cached_at = 0

        def wrapper(*args, **kwargs):
            dt = time.time() - fx.__cached_at
            if (dt > duration and duration is not None) or \
                    (fx.__cached_at == 0 and duration is None):
                val = fx(*args, **kwargs)
                fx.__cached = val
                fx.__cached_at = time.time()
            else:
                val = fx.__cached
            return val
        wrapper.__doc__ = fx.__doc__
        return wrapper
    return decorator


@public
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
    if ajenti.platform_unmapped in values:
        return values[ajenti.platform_unmapped]
    if ajenti.platform in values:
        return values[ajenti.platform]
    return values.get('default', None)


@public
def make_report(e):
    """
    Formats a bug report.
    """
    import platform as _platform
    from ajenti.plugins import manager
    from ajenti import platform, platform_unmapped, platform_string, installation_uid, version, debug

    # Finalize the reported log
    logging.blackbox.stop()

    tb = traceback.format_exc(e)
    tb = '\n'.join('    ' + x for x in tb.splitlines())
    log = logging.blackbox.buffer
    log = '\n'.join('    ' + x for x in log.splitlines())

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
    import requests
    import psutil

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
requests | %s
psutil | %s


%s

Log content:

%s
            """ % (
        version,
        platform, platform_unmapped, platform_string.strip(),
        subprocess.check_output(['uname', '-mp']).strip(),
        '.'.join([str(x) for x in _platform.python_version_tuple()]),
        installation_uid,
        debug,
        catcher_url or 'Failed to upload traceback',
        ', '.join(sorted(manager.get_order())),

        gevent.__version__,
        greenlet.__version__,
        reconfigure.__version__,
        requests.__version__,
        psutil.__version__,

        tb,
        log,
    )
