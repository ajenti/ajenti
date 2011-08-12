MODULES = ['main', 'config']

DEPS =  [
    (['any'],
     [
        ('plugin', 'webserver_common'),
        ('app', 'lighttpd', 'lighttpd')
     ])
]

NAME = 'lighttpd'
PLATFORMS = ['debian', 'centos']
DESCRIPTION = 'lighttpd webserver control plugin'
VERSION = '0:1.1'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
