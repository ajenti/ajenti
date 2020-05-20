import ssl
import socket
import smtplib
from datetime import datetime
from OpenSSL import crypto

now = datetime.now()

def CertLimitSSL(hostname, port):
    """Return standard SSL cert from hostname:port"""
    ctx = ssl.create_default_context()
    s = ctx.wrap_socket(socket.socket(), server_hostname=hostname)
    s.connect((hostname, port))
    cert = crypto.load_certificate(crypto.FILETYPE_ASN1, s.getpeercert(binary_form=True))
    s.close()
    return cert

def CertLimitSTARTTLS(hostname):
    """Return SSL cert from STARTTLS connection at hostname:587"""
    connection = smtplib.SMTP()
    connection.connect(hostname,587)
    connection.starttls()
    cert = crypto.load_certificate(crypto.FILETYPE_ASN1, connection.sock.getpeercert(binary_form=True))
    connection.quit()
    return cert

def checkOnDom(hostname, port='443'):

    port = int(port)
    certDetails = {
        'status': 'danger',
        'hostname': hostname,
        'port':port,
        'url':hostname+":"+str(port),
        'notAfter': None,
        'restTime': '',
        'issuer': None,
        'subject': None,
        'notBefore': None
    }
    
    ## Locale EN to fix
    import locale
    locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')

    try:
        if port == 587:
            cert = CertLimitSTARTTLS(hostname)
        else:
            cert = CertLimitSSL(hostname, port)
        remainingDays = (datetime.strptime(cert.get_notAfter().decode(),"%Y%m%d%H%M%SZ")-now).days
        certDetails['notAfter'] = str(datetime.strptime(cert.get_notAfter().decode(),"%Y%m%d%H%M%SZ"))
        certDetails['notBefore'] = str(datetime.strptime(cert.get_notBefore().decode(),"%Y%m%d%H%M%SZ"))
        certDetails['issuer'] = dict(cert.get_issuer().get_components())
        certDetails['subject'] = dict(cert.get_subject().get_components())

    except ConnectionRefusedError as e:
        certDetails['notAfter'] = 'No reponse from host !'
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
