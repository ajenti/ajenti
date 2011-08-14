MODULES = ['main', 'backend']

DEPS =  [
    (['any'],
     [
        ('app', 'iptables', 'iptables')
     ])
]

NAME = 'IP tables'
PLATFORMS = ['debian', 'arch', 'centos', 'fedora', 'gentoo']
DESCRIPTION = 'Netfilter rules control plugin'
VERSION = '0:1.4'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
