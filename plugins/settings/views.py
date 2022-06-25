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
from aj.api.http import get, post, HttpPlugin

from aj.api.endpoint import endpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @post(r'/api/settings/generate/client-certificate')
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

        with open(aj.config.data['ssl']['certificate'], 'r') as certificate:
            content = certificate.read()
            ca_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, content)
            ca_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, content)

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
        cert.sign(ca_key, 'sha256')

        pkcs = OpenSSL.crypto.PKCS12()
        pkcs.set_certificate(cert)
        pkcs.set_privatekey(key)
        pkcs.set_friendlyname(bytes(data['cn'], encoding="utf-8"))

        return {
            'digest': cert.digest('sha256').decode('utf-8'),
            'name': ','.join(b'='.join(x).decode('utf-8')
                             for x in cert.get_subject().get_components()
                             ),
            'serial': str(cert.get_serial_number()),
            'b64certificate': base64.b64encode(pkcs.export()).decode('utf-8'),
        }

    @post(r'/api/settings/generate/server-certificate')
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
        certificate_path = f'{etc_dir}/ajenti.pem'

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
        cert.sign(key, 'sha256')

        with open(certificate_path, 'wb') as f:
            f.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key))
            f.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))

        return {
            'path': certificate_path,
        }

    @post(r'/api/settings/test/ssl-certificate')
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

        certificate_path = http_context.json_body()['certificate']

        try:
            with open(certificate_path, 'r') as certificate:
                content = certificate.read()
                OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, content)
                OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, content)
        except Exception as e:
            raise EndpointError(None, message=str(e))

        return True
