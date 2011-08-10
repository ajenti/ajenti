MODULES = ['api', 'main', 'meter', 'widget', 's_upstart', 's_arch', 's_bsd', 's_centos', 's_gentoo']

DEPS =  [
    (['centos', 'fedora'],
     [
	('app', 'Service manager', 'chkconfig'),
     ])
]

NAME = 'Services'
PLATFORMS = ['debian', 'arch', 'freebsd', 'centos', 'fedora', 'gentoo']
DESCRIPTION = 'Control system services'
VERSION = '0:1.4'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
