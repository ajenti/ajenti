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


