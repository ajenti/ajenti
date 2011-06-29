MODULES = ['api', 'main', 's_upstart', 's_arch', 's_bsd', 's_centos', 'widget']

DEPS =  [
    (['centos', 'fedora'],
     [
	('app', 'Service manager', 'chkconfig'),
     ])
]

NAME = 'Services'
PLATFORMS = ['debian', 'arch', 'freebsd', 'centos', 'fedora']
DESCRIPTION = 'Control system services'
VERSION = '0:1.1'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
