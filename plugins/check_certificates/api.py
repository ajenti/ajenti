import ssl
import socket
import smtplib
from datetime import datetime
from OpenSSL import crypto

now = datetime.now()

def CertLimitSSL(hostname, port):
    """
    Get the SSL certificate from a host.

    :param hostname: Hostname
    :type hostname: string
    :param port: Port
    :type port: integer
    :return: OpenSSL cert
    :rtype: OpenSSL cert
    """

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    s = ctx.wrap_socket(socket.socket(), server_hostname=hostname)
    s.settimeout(10)
    s.connect((hostname, port))
    cert = crypto.load_certificate(crypto.FILETYPE_ASN1, s.getpeercert(binary_form=True))
    s.close()
    return cert

def CertLimitSTARTTLS(hostname):
    """
    Get the SSL certificate from host with STARTTLS connection on port 587.

    :param hostname: Hostname
    :type hostname: string
    :return: OpenSSL cert
    :rtype: OpenSSL cert
    """

    connection = smtplib.SMTP(hostname, 587)
    connection.starttls()
    cert = crypto.load_certificate(crypto.FILETYPE_ASN1, connection.sock.getpeercert(binary_form=True))
    connection.quit()
    return cert

def checkOnDom(hostname, port='443'):
    """
    Store all details from a certificate into a dict and add a status attribute
    to display a bootstrap class for the time remaining before renew :
    - renew the next 7 days : danger
    - renew the next 14 days: warning
    - renew the next 28 days : info
    - or success

    :param hostname: Hostname
    :type hostname: string
    :param port: Port to test, default 443
    :type port: string
    :return: Dict with all details from the certificate
    :rtype: dict
    """

    port = int(port)
    certDetails = {
        'status': 'danger',
        'hostname': hostname,
        'port':port,
        'url':hostname,
        'notAfter': None,
        'restTime': '',
        'issuer': None,
        'subject': None,
        'notBefore': None
    }

    try:
        if port == 587:
            cert = CertLimitSTARTTLS(hostname)
        else:
            cert = CertLimitSSL(hostname, port)
        remainingDays = (datetime.strptime(cert.get_notAfter().decode(),"%Y%m%d%H%M%SZ")-now).days
        certDetails['notAfter'] = str(datetime.strptime(cert.get_notAfter().decode(),"%Y%m%d%H%M%SZ"))
        certDetails['notBefore'] = str(datetime.strptime(cert.get_notBefore().decode(),"%Y%m%d%H%M%SZ"))

        issuer = cert.get_issuer().get_components()
        # Issuer be like [(b'C', b'US'), (b'O', b"Let's Encrypt"), (b'CN', b'R3')]
        # Extract Organization name
        certDetails['issuer'] = [e[1] for e in issuer if e[0]==b'O'][0].decode()
        certDetails['subject'] = dict(cert.get_subject().get_components())

    except TimeoutError:
        certDetails['notAfter'] = _('Timeout from host !')
        return certDetails
    except socket.gaierror:
        certDetails['notAfter'] = _('Could not resolve hostname !')
        return certDetails
    except socket.timeout:
        certDetails['notAfter'] = _('Timeout from host !')
        return certDetails
    except ssl.CertificateError:
        certDetails['notAfter'] = _('Certificate is not valid !')
        return certDetails
    except ssl.SSLError:
        certDetails['notAfter'] = _('Can not handle SSL on this port !')
        return certDetails
    except ConnectionRefusedError:
        certDetails['notAfter'] = _('Host refuse the connection !')
        return certDetails

    if remainingDays <= 7:
        certDetails['restTime'] = '< 7'
    elif remainingDays <= 14:
        certDetails['status'] = 'warning'
        certDetails['restTime'] = '< 14'
    elif remainingDays <= 28:
        certDetails['status'] = 'info'
        certDetails['restTime'] = '< 28'
    else:
        certDetails['status'] = 'success'

    return certDetails
