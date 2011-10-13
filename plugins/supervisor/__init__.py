MODULES = ['main', 'widget']

DEPS =  [
    (['any'],
     [
        ('app', 'Supervisor console', 'supervisorctl'),
   		('plugin', 'services'),
     ])
]

NAME = 'Supervisor'
PLATFORMS = ['any']
DESCRIPTION = 'Control processes under supervisord'
VERSION = '0'
GENERATION = 1
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
