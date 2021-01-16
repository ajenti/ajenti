"""
This module handles server and client certificates for ajenti.
"""

import json
import random
import socket
import OpenSSL.crypto
import base64

import aj
from jadi import component
from aj.api.http import url, HttpPlugin

from aj.api.endpoint import endpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/settings/generate-client-certificate')
    @endpoint(api=True)
    def handle_api_generate_client_certificate(self, http_context):
        """
        Generate new client certificate based on settings informations.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Certificates informations (serial, digest, ...)
        :rtype: dict
        """

        data = json.loads(http_context.body.decode())

        key = OpenSSL.crypto.PKey()
        key.generate_key(OpenSSL.crypto.TYPE_RSA, 4096)
        ca_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, open(aj.config.data['ssl']['certificate']).read())
        ca_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(aj.config.data['ssl']['certificate']).read())
        cert = OpenSSL.crypto.X509()
        cert.get_subject().countryName = data['c']
        cert.get_subject().stateOrProvinceName = data['st']
        cert.get_subject().organizationName = data['o']
        cert.get_subject().commonName = data['cn']
        cert.set_pubkey(key)
        cert.set_serial_number(random.getrandbits(8 * 20))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
        cert.set_issuer(ca_cert.get_subject())
        cert.sign(ca_key, 'sha1')

        pkcs = OpenSSL.crypto.PKCS12()
        pkcs.set_certificate(cert)
        pkcs.set_privatekey(key)
        pkcs.set_friendlyname(bytes(data['cn'], encoding="utf-8"))

        return {
            'digest': cert.digest('sha1').decode('utf-8'),
            'name': ','.join(b'='.join(x).decode('utf-8')
                             for x in cert.get_subject().get_components()
                             ),
            'serial': str(cert.get_serial_number()),
            'b64certificate': base64.b64encode(pkcs.export()).decode('utf-8'),
        }

    @url(r'/api/settings/generate-server-certificate')
    @endpoint(api=True)
    def handle_api_generate_server_certificate(self, http_context):
        """
        Generate a new server certificate for a SSL connection to ajenti server.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Certificate path commonly /etc/ajenti/ajenti.pem
        :rtype: dict
        """

        etc_dir = '/etc/ajenti'
        certificate_path = '%s/ajenti.pem' % etc_dir

        key = OpenSSL.crypto.PKey()
        key.generate_key(OpenSSL.crypto.TYPE_RSA, 4096)
        cert = OpenSSL.crypto.X509()
        cert.get_subject().countryName = 'NA'
        cert.get_subject().organizationName = socket.gethostname()
        cert.get_subject().commonName = 'ajenti'
        cert.set_pubkey(key)
        cert.set_serial_number(random.getrandbits(8 * 20))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.sign(key, 'sha1')

        with open(certificate_path, 'wb') as f:
            f.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key))
            f.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))

        return {
            'path': certificate_path,
        }

    @url(r'/api/settings/test-certificate/')
    @endpoint(api=True)
    def handle_test_certificate(self, http_context):
        """
        Try to load the specified certificate in order to test if it is valid
        or not.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Certificate path, commonly in /etc/ajenti
        :rtype: dict
        """

        if http_context.method == 'POST':
            data = http_context.json_body()
            certificate_path = data['certificate']
            try:
                OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(certificate_path).read())
                OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, open(certificate_path).read())
            except Exception as e:
                raise EndpointError(None, message=str(e))    
                
            return {'path': certificate_path}
