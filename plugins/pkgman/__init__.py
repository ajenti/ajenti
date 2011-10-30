MODULES = ['api', 'main', 'component', 'pm_apt', 'pm_pacman', 'pm_portage', 'pm_ports',  'pm_yum']

DEPS =  [
    (['debian'],
     [
        ('app', 'dpkg', 'dpkg')
     ]),
    (['arch'],
     [
        ('app', 'pacman', 'pacman')
     ]),
    (['centos', 'fedora'],
     [
        ('app', 'yum', 'yum')
    ]),
    (['freebsd'],
     [
        ('app', 'pkg-tools', 'portupgrade')
    ]),
    (['gentoo'],
     [
        ('app', 'eix', 'eix'),
     ]),
]

NAME = 'Package manager'
PLATFORMS = ['debian', 'arch', 'freebsd', 'centos', 'fedora', 'gentoo']
DESCRIPTION = 'Manage software packages'
VERSION = '1'
GENERATION = 1
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
