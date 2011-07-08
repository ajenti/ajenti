MODULES = ['ui_sarg']

DEPS =  [
    (['any'],
     [
        ('plugin', 'squid'),
        ('app', 'SARG', 'sarg')
     ])
]

NAME = 'SARG'
PLATFORMS = ['any']
DESCRIPTION = 'Control Squid report generator'
VERSION = '0:1.1'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
