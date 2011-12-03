import time

from ajenti.com import *
from ajenti.ui import *
from ajenti.utils import shell, str_fsize


class LinuxIfconfig(Plugin):
    platform = ['Debian', 'Ubuntu', 'Arch', 'openSUSE']
    
    def get_info(self, iface):
        ui = UI.LayoutTable(
                UI.LayoutTableRow(
                    UI.Image(file='/dl/network/%s.png'%('up' if iface.up else 'down')),
                    UI.Label(text='Interface:', bold=True),
                    UI.Label(text=iface.name, bold=True)
                ),
                UI.LayoutTableRow(
                    UI.Label(),
                    UI.Label(text='Address:'),
                    UI.Label(text=self.get_ip(iface))
                ),
                UI.LayoutTableRow(
                    UI.Label(),
                    UI.Label(text='Sent:'),
                    UI.Label(text=str_fsize(self.get_tx(iface)))
                ),
                UI.LayoutTableRow(
                    UI.Label(),
                    UI.Label(text='Received:'),
                    UI.Label(text=str_fsize(self.get_rx(iface)))
                )
            )
           
        return ui
        
    def get_tx(self, iface):
        try:
            return int(shell('ifconfig %s | grep \'TX bytes\''%iface.name).split()[5].split(':')[1])
        except: pass
        
        try:
            return int(shell('ifconfig %s | grep -E \'TX .+ bytes\''%iface.name).split()[4])
        except: pass
        
        return 0
    
    def get_rx(self, iface):
        try:
            return int(shell('ifconfig %s | grep \'RX bytes\''%iface.name).split()[1].split(':')[1])
        except: pass
        
        try:
            return int(shell('ifconfig %s | grep -E \'RX .+ bytes\''%iface.name).split()[4])
        except: pass
        
        return 0
        
    def get_ip(self, iface):
        try:
            return shell('ifconfig %s | grep \'inet addr\''%iface.name).split()[1].split(':')[1]
        except: pass

        try:
            return shell('ifconfig %s | grep \'inet\''%iface.name).split()[1]
        except: pass
        
        return '0.0.0.0'

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
        return ''

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
        shell('ifconfig %s up' % iface.name)
        time.sleep(1)

    def down(self, iface):
        shell('ifconfig %s down' % iface.name)
        time.sleep(1)
        