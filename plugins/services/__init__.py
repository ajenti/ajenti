MODULES = ['api', 'main', 's_upstart', 's_arch', 's_bsd', 's_centos', 's_gentoo']

DEPS =  [
    (['centos', 'fedora'],
     [
	('app', 'Service manager', 'chkconfig'),
     ])
]

NAME = 'Services'
PLATFORMS = ['debian', 'arch', 'freebsd', 'centos', 'fedora', 'gentoo']
DESCRIPTION = 'Control system services'
VERSION = '0:1.0'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
