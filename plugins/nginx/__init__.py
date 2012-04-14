MODULES = ['main', 'main_single', 'config']

DEPS =  [
    (['any'],
     [
        ('plugin', 'webserver_common'),
        ('app', 'nginx', 'nginx')
     ])
]

NAME = 'nginx'
PLATFORMS = ['debian', 'arch', 'freebsd', 'gentoo', 'centos', 'mandriva']
DESCRIPTION = 'nginx webserver control plugin'
VERSION = '1'
GENERATION = 1
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
