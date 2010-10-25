MODULES = ['api', 'main', 'pm_apt', 'pm_zypper', 'pm_pacman', 'pm_ports', 'pm_cluster']

DEPS =  [
    (['debian'],
     [
        ('app', 'dpkg', 'dpkg')
     ]),
    (['opensuse'],
     [
        ('app', 'zypper', 'zypper')
     ]),
    (['arch'],
     [
        ('app', 'pacman', 'pacman')
     ])
]

NAME = 'pkgman'
PLATFORMS = ['debian', 'arch', 'opensuse', 'freebsd']
DESCRIPTION = 'Manage software packages'
VERSION = '0.1'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
