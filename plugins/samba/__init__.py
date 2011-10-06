MODULES = ['backend', 'main']

DEPS =  [
    (['any'],
     [
    	('app', 'Samba', 'smbd'),
        ('plugin', 'services'),
     ])
]

NAME = 'Samba'
PLATFORMS = ['any']
DESCRIPTION = 'Control Samba server'
VERSION = '0:1.2'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
