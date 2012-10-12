import traceback
import logging


def str_fsize(sz):
    """
    Formats file size as string (1.2 Mb)
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
