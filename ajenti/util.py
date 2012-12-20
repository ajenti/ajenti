import traceback
import logging
import time


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


def str_timedelta(s):
    """
    Formats a time delta (i.e., "5 days, 5:06:07")
    """
    d60 = lambda x: ('0' if (x % 60) < 10 else '') + str(x % 60)
    s = int(s)
    r = '%s:%s:%s' % (d60(s / 3600), d60(s / 60), d60(s))
    s /= 3600 * 24
    if s > 0:
        r = '%i days, ' % s + r
    return r


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
        return wrapper
    return decorator


def make_report():
    """
    Formats a bug report.
    """
    import platform as _platform
    from ajenti.plugins import manager
    from ajenti import platform, platform_string, platform_unmapped, installation_uid, version, debug

    # Finalize the reported log
    logging.blackbox.stop()

    return (('Ajenti %s bug report\n' +
           '--------------------\n\n' +
           'Detected platform: %s / %s / %s\n' +
           'Python: %s\n' +
           'Installation: %s\n' +
           'Debug: %s\n' +
           'Loaded plugins:\n%s\n\n' +
           '%s\n\n'
           'Log:\n%s\n'
           )
            % (version,
               platform, platform_unmapped, platform_string,
               '.'.join([str(x) for x in _platform.python_version_tuple()]),
               installation_uid,
               debug,
               ' '.join(manager.get_order()),
               traceback.format_exc(),
               logging.blackbox.buffer,
              ))
