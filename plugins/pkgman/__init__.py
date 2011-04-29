MODULES = ['api', 'main', 'component', 'pm_apt', 'pm_pacman', 'pm_ports',  'pm_yum']

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
    ])
]

NAME = 'Package manager'
PLATFORMS = ['debian', 'arch', 'freebsd', 'centos', 'fedora']
DESCRIPTION = 'Manage software packages'
VERSION = '0:1.0'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
