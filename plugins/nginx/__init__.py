MODULES = ['main', 'config']

DEPS =  [
    (['any'],
     [
        ('plugin', 'webserver_common'),
        ('app', 'nginx', 'nginx')
     ])
]

NAME = 'nginx'
PLATFORMS = ['debian', 'arch']
DESCRIPTION = 'nginx webserver control plugin'
VERSION = '0:1.1'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
