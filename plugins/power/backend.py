import re
import os


class ACAdapter:
    present = False
    name = ''


def get_ac_adapters():
    r = []
    
    try:
        lst = []
        lst = os.listdir('/proc/acpi/ac_adapter')
    except:
        pass
        
    for x in lst:
        try:
            a = ACAdapter()
            a.name = x
            ss = open('/proc/acpi/ac_adapter/%s/state' % x).read().split('\n')
            for s in ss:
                if s.startswith('state:'):
                    a.present = s.endswith('on-line')
            r.append(a)
        except:
            pass
    return r


class Battery:
    present = False
    name = ''
    charge = 0
    total = 0
    current = 0


def get_batteries():
    r = []
    
    try:
        lst = []
        lst = os.listdir('/proc/acpi/battery')
    except:
        pass
        
    for x in lst:
        try:
            b = Battery()
            b.name = x
            b.total = 10000
            b.current = 10000
            ss = open('/proc/acpi/battery/%s/state' % x).read().split('\n')
            for s in ss:
                if s.startswith('present:'):
                    b.present = s.endswith('yes')
                if s.startswith('remaining capacity:'):
                    b.current = int(s.split()[2])
            ss = open('/proc/acpi/battery/%s/info' % x).read().split('\n')
            for s in ss:
                if s.startswith('design capacity:'):
                    b.total = int(s.split()[2])
            b.charge = int(b.current * 100 / b.total)
            r.append(b)
        except:
            pass
    return r


def get_uptime():
    minute = 60
    hour = minute * 60
    day = hour * 24

    d = h = m = 0

    try:
        s = int(open('/proc/uptime').read().split('.')[0])

        d = s / day
        s -= d * day
        h = s / hour
        s -= h * hour
        m = s / minute
        s -= m * minute
    except IOError:
        # Try use 'uptime' command
        up = os.popen('uptime').read()
        if up:
            uptime = re.search('up\s+(.*?),\s+[0-9]+ user',up).group(1)
            return uptime

    uptime = ""
    if d > 1:
        uptime = "%d days, "%d
    elif d == 1:
        uptime = "1 day, "

    return uptime + "%d:%02d:%02d"%(h,m,s)
