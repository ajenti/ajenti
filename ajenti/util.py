import traceback
import subprocess
import logging
import time
import sys
import fcntl
import locale
import os
import catcher

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
        return '%.1f Kb' % sz
    sz /= 1024.0
    if sz < 1024:
        return '%.1f Mb' % sz
    sz /= 1024.0
    return '%.1f Gb' % sz


@public
def str_timedelta(s):
    """
    Formats a time delta (i.e., "5 days, 5:06:07")
    """
    d60 = lambda x: ('0' if (x % 60) < 10 else '') + str(x % 60)
    s = int(s)
    r = '%s:%s:%s' % (d60(s / 3600 % 24), d60(s / 60), d60(s))
    s /= 3600 * 24
    if s > 0:
        r = '%i days, ' % s + r
    return r


@public
def cache_value(duration):
    """
    Makes a function lazy.

    :param duration: cache duration in seconds
    """
    def decorator(fx):
        fx.__cached = None
        fx.__cached_at = 0

        def wrapper(*args, **kwargs):
            if time.time() - fx.__cached_at > duration:
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
    Selects a value from **kwargs depending on runtime platform::

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
    
    catcher_url = None
    try:
        report = catcher.collect(e)
        html = catcher.formatters.HTMLFormatter().format(report, maxdepth=3)
        catcher_url = catcher.uploaders.AjentiOrgUploader().upload(html)
    except:
        pass

    return """Ajenti %s bug report
--------------------
Detected platform: %s / %s / %s
Architecture: %s
Python: %s
Installation: %s
Debug: %s
Locale: %s
Loaded plugins:
%s

%s
%s

Log content:
%s
            """ % (
        version,
        platform, platform_unmapped, platform_string,
        subprocess.check_output(['uname', '-mp']),
        '.'.join([str(x) for x in _platform.python_version_tuple()]),
        installation_uid,
        debug,
        locale.getlocale(locale.LC_MESSAGES),
        ' '.join(manager.get_order()),
        tb,
        catcher_url or 'Failed to upload traceback',
        logging.blackbox.buffer,
    )


@public
class PidFile(object):
    """
    Context manager that locks a pid file.  Implemented as class
    not generator because daemon.py is calling .__exit__() with no parameters
    instead of the None, None, None specified by PEP-343.
    """

    def __init__(self, path):
        self.path = path
        self.pidfile = None

    def __enter__(self):
        self.pidfile = open(self.path, "a+")
        try:
            fcntl.flock(self.pidfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            raise SystemExit("Already running according to " + self.path)
        self.pidfile.seek(0)
        self.pidfile.truncate()
        self.pidfile.write(str(os.getpid()))
        self.pidfile.flush()
        self.pidfile.seek(0)
        return self.pidfile

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        try:
            self.pidfile.close()
        except IOError as err:
            # ok if file was just closed elsewhere
            if err.errno != 9:
                raise
        os.remove(self.path)
