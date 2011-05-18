MODULES = ['main', 'main_single', 'config']

DEPS =  [
    (['centos'],
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
PLATFORMS = ['any']
DESCRIPTION = 'Apache webserver control plugin'
VERSION = '0:1.0'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
