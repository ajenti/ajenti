import json
import random
import socket
from OpenSSL.crypto import *

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
        data = json.loads(http_context.body)

        key = PKey()
        key.generate_key(TYPE_RSA, 4096)
        ca_key = load_privatekey(FILETYPE_PEM, open(aj.config.data['ssl']['certificate']).read())
        ca_cert = load_certificate(FILETYPE_PEM, open(aj.config.data['ssl']['certificate']).read())
        cert = X509()
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

        pkcs = PKCS12()
        pkcs.set_certificate(cert)
        pkcs.set_privatekey(key)
        pkcs.set_friendlyname(str(data['cn']))

        return {
            'digest': cert.digest('sha1'),
            'name': ','.join('%s=%s' % x for x in cert.get_subject().get_components()),
            'serial': cert.get_serial_number(),
            'b64certificate': pkcs.export().encode('base64'),
        }

    @url(r'/api/settings/generate-server-certificate')
    @endpoint(api=True)
    def handle_api_generate_server_certificate(self, http_context):
        etc_dir = '/etc/ajenti'
        certificate_path = '%s/ajenti.pem' % etc_dir

        key = PKey()
        key.generate_key(TYPE_RSA, 4096)
        cert = X509()
        cert.get_subject().countryName = 'NA'
        cert.get_subject().organizationName = socket.gethostname()
        cert.get_subject().commonName = 'ajenti'
        cert.set_pubkey(key)
        cert.set_serial_number(random.getrandbits(8 * 20))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.sign(key, 'sha1')

        with open(certificate_path, 'w') as f:
            f.write(dump_privatekey(FILETYPE_PEM, key))
            f.write(dump_certificate(FILETYPE_PEM, cert))

        return {
            'path': certificate_path,
        }
