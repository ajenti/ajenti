import time

from ajenti.com import *
from ajenti.ui import *
from ajenti.utils import shell, str_fsize


class BSDIfconfig(Plugin):
    platform = ['FreeBSD']
    
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
        s = shell('netstat -bI %s | grep -v Link | grep -v pkts'%iface.name)
        print s
        try:
            s = s.split()[10]
        except:
            s = '0'
        return int(s)
    
    def get_rx(self, iface):
        s = shell('netstat -bI %s | grep -v Link | grep -v pkts'%iface.name)
        print s
        try:
            s = s.split()[7]
        except:
            s = '0'
        return int(s)
        
    def get_ip(self, iface):
        s = shell('ifconfig %s | grep \'inet \''%iface.name)
        try:
            s = s.split()[1]
        except:
            s = '0.0.0.0'
        return s    
        

    def detect_dev_class(self, iface):
        if iface.name[:-1] == 'gif':
            return 'tunnel'
        if iface.name == 'lo':
            return 'loopback'
        if iface.name[:-1] == 'em':
            return 'ethernet'
        return ''

    def detect_iface_bits(self, iface):
        r = ['bsd-basic']
        cls = self.detect_dev_class(iface)
        if iface.addressing == 'static':
            r.append('bsd-ipv4')
        if cls == 'tunnel':
            r.append('bsd-tunnel')
        return r
        
    def up(self, iface):
        shell('ifconfig %s up' % iface.name)
        time.sleep(1)

    def down(self, iface):
        shell('ifconfig %s down' % iface.name)
        time.sleep(1)
        