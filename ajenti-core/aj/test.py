import os


def start():
    import sys
    print('in modules?', 'os' in sys.modules)
    print('in globals?', 'os' in globals())
    print('in locals?', 'os' in locals())
    print('os =', os)

    import os.path
    os.path.exists('useless statement')


start()
