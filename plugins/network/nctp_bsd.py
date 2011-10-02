import time

from ajenti.com import *
from ajenti.ui import *
from ajenti.utils import shell, str_fsize


class BSDIfconfig(Plugin):
    platform = ['FreeBSD']
    
    def get_info(self, iface):
        ui = UI.Container(
                UI.Formline(
                    UI.HContainer(
                        UI.Image(file='/dl/network/%s.png'%('up' if iface.up else 'down')),
                        UI.Label(text=iface.name, bold=True)
                    ),
                    text='Interface',
                ),
                UI.Formline(
                    UI.Label(text=self.get_ip(iface)),
                    text='Address',
                ),
                UI.Formline(
                    UI.Label(text='Up %s, down %s' % (
                    str_fsize(self.get_tx(iface)),
                        str_fsize(self.get_rx(iface)),
                    )),
                    text='Traffic',
                ),
            )
           
        return ui
        
    def get_tx(self, iface):
        s = shell('netstat -bI %s | grep -v Link | grep -v pkts'%iface.name)
        try:
            s = s.split()[10]
        except:
            s = '0'
        return int(s)
    
    def get_rx(self, iface):
        s = shell('netstat -bI %s | grep -v Link | grep -v pkts'%iface.name)
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
        return 'ethernet'

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
        
