import fcntl
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

    try:
        inet_line = subprocess.check_output(
            f"ip -4 addr show {iface} | grep 'inet '",
            shell=True,
            encoding='utf-8'
        )
        return inet_line.strip().split()[1].split('/')
    except subprocess.CalledProcessError as e:
        # No ipv4 found
        return ["Not configured"]*2

def ifconfig_get_ip6_mask(iface):
    """
    Get ipv6 and mask of an interface from the ip addr command.

    :param iface: Network interface, e.g. eth0
    :type iface: string
    :return: ip,mask
    :rtype: tuple
    """

    try:
        inet_line = subprocess.check_output(
            f"ip -6 addr show {iface} | grep 'inet6 '",
            shell=True,
            encoding='utf-8'
        )
        return inet_line.strip().split()[1].split('/')
    except subprocess.CalledProcessError as e:
        # No ipv6 found
        return ["Not configured"]*2

def ifconfig_get_gateway(iface):
    """
    Get gateway of an interface from the ip addr command.

    :param iface: Network interface, e.g. eth0
    :type iface: string
    :return: gateway
    :rtype: string
    """

    return subprocess.check_output(
        f"ip route | grep default | grep {iface} | cut -d' ' -f3",
        shell=True,
        encoding='utf-8'
    )


def ifconfig_get_up(iface):
    """
    Check the iface status.

    :param iface: Network interface, e.g. eth0
    :type iface: string
    :return: If the iface is up or not
    :rtype: bool
    """

    if subprocess.call(['ip', 'l', 'show', iface]) != 0:
        return False
    return b'UP' in subprocess.check_output(['ip', 'l', 'show', iface])


def ifconfig_up(iface):
    """
    Bring a network interface up.

    :param iface: Network interface, e.g. eth0
    :type iface: string
    """

    subprocess.check_call(['ip', 'link', 'set', iface, 'up'])
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
    subprocess.check_call(['ip', 'link', 'set', iface, 'down'])
