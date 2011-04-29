MODULES = ['main', 'config', 'recovery']

DEPS =  [
    (['any'],
     [
        ('plugin', 'webserver_common'),
        ('app', 'lighttpd', 'lighttpd')
     ])
]

NAME = 'lighttpd'
PLATFORMS = ['any']
DESCRIPTION = 'lighttpd webserver control plugin'
VERSION = '0:1.0'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
