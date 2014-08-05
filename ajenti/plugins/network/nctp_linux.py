import fcntl
import gevent
import subprocess
import socket
import struct
import re

from ajenti.api import *
from ajenti.ui import *


class LinuxIfconfig (object):
    platforms = ['debian', 'centos', 'mageia']

    def detect_dev_class(self, iface):
        ifname = re.compile('[a-z]+').findall(iface.name)
        if not ifname: 
            return 'ethernet'
        ifname = ifname[0]
        if ifname in ['ppp', 'wvdial']:
            return 'ppp'
        if ifname in ['wlan', 'ra', 'wifi', 'ath']:
            return 'wireless'
        if ifname == 'br':
            return 'bridge'
        if ifname == 'tun':
            return 'tunnel'
        if ifname == 'lo':
            return 'loopback'
        if ifname == 'eth':
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
        gevent.sleep(1)

    def down(self, iface):
        subprocess.call(['ifdown', iface.name])
        gevent.sleep(1)

    def get_ip(self, iface):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', iface.name[:15]))[20:24])
        except IOError:
            return None
