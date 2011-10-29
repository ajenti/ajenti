MODULES = ['main_single', 'config']

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
VERSION = '0'
GENERATION = 1
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
