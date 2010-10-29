MODULES = ['api', 'main', 'pm_apt', 'pm_zypper', 'pm_pacman', 'pm_ports',  'pm_yum', 'pm_cluster']

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
     ]),
    (['centos', 'fedora'],
     [
        ('app', 'yum', 'yum')
    ])
]

NAME = 'Package manager'
PLATFORMS = ['debian', 'arch', 'opensuse', 'freebsd', 'centos', 'fedora']
DESCRIPTION = 'Manage software packages'
VERSION = '0.1'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
