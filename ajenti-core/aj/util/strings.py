def str_fsize(sz):
    """
    Formats file size as string (i.e., 1.2 Mb)
    """
    if sz < 1024:
        return f'{sz:.1f} bytes'
    sz /= 1024.0
    if sz < 1024:
        return f'{sz:.1f} KB'
    sz /= 1024.0
    if sz < 1024:
        return f'{sz:.1f} MB'
    sz /= 1024.0
    if sz < 1024:
        return f'{sz:.1f} GB'
    sz /= 1024.0
    return f'{sz:.1f} TB'


