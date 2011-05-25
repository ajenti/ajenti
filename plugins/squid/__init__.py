MODULES = ['api', 'config', 'backend', 'main', 'ui_acls', 'ui_bindings', 'ui_http_access', 'ui_refresh_patterns']

DEPS =  [
    (['any'],
     [
        ('plugin', 'services'),
        ('app', 'Squid', 'squid')
     ])
]

NAME = 'Squid'
PLATFORMS = ['any']
DESCRIPTION = 'Control Squid caching proxy server'
VERSION = '0:1.1'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
