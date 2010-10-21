MODULES = ['api', 'widget', 'ss_linux', 'ss_bsd']

DEPS =  [
    (['freebsd'],
     [
        ('app', 'sysutils/freecolor', 'freecolor'),
     ])
]

NAME = 'System Load'
DESCRIPTION = 'CPU load and memory usage widgets for dashboard'
VERSION = '0.1'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
