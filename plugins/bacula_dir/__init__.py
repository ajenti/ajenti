MODULES = ['main', 'backend']

DEPS =  [
    (['any'],
     [
        ('plugin', 'services'),
        ('plugin', 'bacula_common'),
        ('app', 'Bacula Director', 'bacula-dir')
     ])
]
NAME = 'Bacula Director'
PLATFORMS = ['any']
DESCRIPTION = 'Director configurator and manager'
VERSION = '0'
GENERATION = 1
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
