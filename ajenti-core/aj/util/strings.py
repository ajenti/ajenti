from datetime import timedelta


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


def str_timedelta(s):
    """
    Formats a time delta (i.e., "5 days, 5:06:07")
    """
    return str(timedelta(0, s)).split('.')[0]
