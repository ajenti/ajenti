import fcntl
import shutil
import socket
import struct
import subprocess


def ifconfig_get_ip(iface):
    """
    Return the ip of a network interface.

    :param iface: Network interface, e.g. eth0
    :type iface: string
    :return: ip
    :rtype: string
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', iface[:15].encode('utf-8')))[20:24])
    except IOError:
        return None


def ifconfig_get_ip4_mask(iface):
    """
    Get ipv4 and mask of an interface from the ip addr command.

    :param iface: Network interface, e.g. eth0
    :type iface: string
    :return: ip,mask
    :rtype: tuple
    """

    ip_path = shutil.which('ip') or 'ip'
    try:
        out = subprocess.check_output([ip_path, '-4', 'addr', 'show', iface], encoding='utf-8')
        for line in out.splitlines():
            if 'inet ' in line:
                return line.strip().split()[1].split('/')
    except (subprocess.CalledProcessError, IndexError):
        # No ipv4 found or parsing error
        pass
    return ['Not configured'] * 2


def ifconfig_get_ip6_mask(iface):
    """
    Get ipv6 and mask of an interface from the ip addr command.

    :param iface: Network interface, e.g. eth0
    :type iface: string
    :return: ip,mask
    :rtype: tuple
    """

    ip_path = shutil.which('ip') or 'ip'
    try:
        out = subprocess.check_output([ip_path, '-6', 'addr', 'show', iface], encoding='utf-8')
        for line in out.splitlines():
            if 'inet6 ' in line:
                return line.strip().split()[1].split('/')
    except (subprocess.CalledProcessError, IndexError):
        # No ipv6 found or parsing error
        pass
    return ['Not configured'] * 2


def ifconfig_get_gateway(iface):
    """
    Get gateway of an interface from the ip addr command.

    :param iface: Network interface, e.g. eth0
    :type iface: string
    :return: gateway
    :rtype: string
    """

    ip_path = shutil.which('ip') or 'ip'
    try:
        out = subprocess.check_output([ip_path, 'route'], encoding='utf-8')
        for line in out.splitlines():
            if 'default' in line and iface in line:
                parts = line.split()
                if 'via' in parts:
                    return parts[parts.index('via') + 1]
    except (subprocess.CalledProcessError, ValueError, IndexError):
        pass
    return ''


def ifconfig_get_up(iface):
    """
    Check the iface status.

    :param iface: Network interface, e.g. eth0
    :type iface: string
    :return: If the iface is up or not
    :rtype: bool
    """

    ip_path = shutil.which('ip') or 'ip'
    if subprocess.call([ip_path, 'l', 'show', iface]) != 0:
        return False
    return b'UP' in subprocess.check_output([ip_path, 'l', 'show', iface])


def ifconfig_up(iface):
    """
    Bring a network interface up.

    :param iface: Network interface, e.g. eth0
    :type iface: string
    """

    ip_path = shutil.which('ip') or 'ip'
    subprocess.check_call([ip_path, 'link', 'set', iface, 'up'])
    ### Is it necessary to do something else like set ip/mask/gateway/post-script ... ?
    # if subprocess.call(['which', 'ifup']) == 0:
        # subprocess.check_call(['ifup', iface])


def ifconfig_down(iface):
    """
    Bring a network interface down.

    :param iface: Network interface, e.g. eth0
    :type iface: string
    """

    ### Is it necessary to do something else ?
    # if subprocess.call(['which', 'ifdown']) == 0:
        # subprocess.check_call(['ifdown', iface])
    ip_path = shutil.which('ip') or 'ip'
    subprocess.check_call([ip_path, 'link', 'set', iface, 'down'])
