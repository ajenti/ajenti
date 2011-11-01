MODULES = ['main', 'main_single', 'config']

DEPS =  [
    (['centos', 'arch', 'freebsd', 'mandriva'],
     [
        ('plugin', 'webserver_common'),
        ('app', 'Apache 2', 'httpd'),
     ]),
    (['any'],
     [
        ('plugin', 'webserver_common'),
        ('app', 'Apache 2', 'apache2'),
     ])
]

NAME = 'Apache'
PLATFORMS = ['centos', 'arch', 'freebsd', 'debian', 'mandriva']
DESCRIPTION = 'Apache webserver control plugin'
VERSION = '0'
GENERATION = 1
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
