import time
import subprocess

from ajenti.api import *
from ajenti.ui import *


@plugin
class LinuxIfconfig (object):
    platforms = ['debian', 'centos']

    def detect_dev_class(self, iface):
        if iface.name[:-1] in ['ppp', 'wvdial']:
            return 'ppp'
        if iface.name[:-1] in ['wlan', 'ra', 'wifi', 'ath']:
            return 'wireless'
        if iface.name[:-1] == 'br':
            return 'bridge'
        if iface.name[:-1] == 'tun':
            return 'tunnel'
        if iface.name == 'lo':
            return 'loopback'
        if iface.name[:-1] == 'eth':
            return 'ethernet'
        return 'ethernet'

    def detect_iface_bits(self, iface):
        r = ['linux-basic']
        cls = self.detect_dev_class(iface)
        if iface.type == 'inet' and iface.addressing == 'static':
            r.append('linux-ipv4')
        if iface.type == 'inet6' and iface.addressing == 'static':
            r.append('linux-ipv6')
        if iface.addressing == 'dhcp':
            r.append('linux-dhcp')
        if cls == 'ppp':
            r.append('linux-ppp')
        if cls == 'wireless':
            r.append('linux-wlan')
        if cls == 'bridge':
            r.append('linux-bridge')
        if cls == 'tunnel':
            r.append('linux-tunnel')

        r.append('linux-ifupdown')
        return r

    def up(self, iface):
        subprocess.call(['ifup', iface.name])
        time.sleep(1)

    def down(self, iface):
        subprocess.call(['ifdown', iface.name])
        time.sleep(1)
