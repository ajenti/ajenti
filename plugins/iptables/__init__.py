MODULES = ['main', 'backend']

DEPS =  [
    (['any'],
     [
        ('app', 'iptables', 'iptables')
     ])
]

NAME = 'IP tables'
PLATFORMS = ['debian', 'arch', 'centos', 'fedora']
DESCRIPTION = 'Netfilter rules control plugin'
VERSION = '0:1.3'
AUTHOR = 'Ajenti team'
HOMEPAGE = 'http://ajenti.org'
