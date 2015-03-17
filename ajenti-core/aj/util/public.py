import sys


def public(f):
    """"
    Use a decorator to avoid retyping function/class names.

    Based on an idea by Duncan Booth:
    http://groups.google.com/group/comp.lang.python/msg/11cbb03e09611b8a

    Improved via a suggestion by Dave Angel:
    http://groups.google.com/group/comp.lang.python/msg/3d400fb22d8a42e1

    """
    _all = sys.modules[f.__module__].__dict__.setdefault('__all__', [])
    if f.__name__ not in _all:  # Prevent duplicates if run from an IDE.
        _all.append(f.__name__)
    return f
