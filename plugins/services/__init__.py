MODULES = ['api', 'main', 's_upstart', 's_arch', 's_suse', 's_bsd']

DEPS =  [
    (['opensuse'],
     [
        ('app', 'Service manager', 'chkconfig'),
     ])
]

NAME = 'Services'
PLATFORMS = ['any']
DESCRIPTION = 'Control system services'
VERSION = '0.6'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
