from jadi import service
import aj
import logging


@service
class ClientCertificateVerificator():
    def __init__(self, context):
        self.context = context

    def verify(self, x509):
        serial = x509.get_serial_number()
        digest = x509.digest('sha256')
        if not b'sha256' in x509.get_signature_algorithm():
            logging.warning(
                f'Sha1 digest algorithm is deprecated,'
                f'you should revoke the client certificate with serial {serial}'
                f'and create a new one.')
        # logging.debug(f'SSL verify: {x509.get_subject()} / {digest}')
        for c in aj.config.data['ssl']['client_auth']['certificates']:
            if int(c['serial']) == serial and c['digest'].encode('utf-8') == digest:
                return c['user']
