MODULES = ['main', 'recovery']

DEPS =  [
    (['any'],
     [
        ('plugin', 'webserver_common'),
        ('app', 'nginx', 'nginx')
     ])
]

NAME = 'nginx'
PLATFORMS = ['any']
DESCRIPTION = 'nginx webserver control plugin'
VERSION = '0.1'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
