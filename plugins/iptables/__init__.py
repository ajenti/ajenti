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
VERSION = '0'
GENERATION = 1
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
