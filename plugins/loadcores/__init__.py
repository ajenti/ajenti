MODULES = ['api', 'meters', 'widget', 'ss_linux']

DEPS =  [
    (['any'],
     [
        ('app', 'mpstat', 'mpstat')
     ])
]

NAME = 'CPU Load Cores'
PLATFORMS = ['debian', 'arch', 'freebsd', 'centos', 'fedora', 'gentoo']
DESCRIPTION = 'CPU load cores usage widgets for dashboard'
VERSION = '1.0.0'
GENERATION = 1
AUTHOR = 'Kolesnik Artem'
HOMEPAGE = 'http://vk.com/kolesnik.artem'
