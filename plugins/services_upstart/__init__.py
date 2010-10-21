MODULES = ['main']

DEPS =  [
    (['ubuntu', 'debian'],
     [
        ('app',     'Upstart', 'service'),
        ('plugin',  'services')
     ])
]

NAME = 'Upstart'
DESCRIPTION = 'Upstart backend for services plugin'
VERSION = '1.0'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
