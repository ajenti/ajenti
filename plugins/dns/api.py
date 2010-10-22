from ajenti.com import *


class IDNSConfig(Interface):
    nameservers = None

    def save(self):
        pass


class Nameserver:
    cls = ''
    address = ''
