import qrcode
import pyotp
import base64
import re
from io import BytesIO


def is_valid_totp_entry(entry):
    """
    Check an entry of the totp list in tfa.yml, as built by the TOTP settings
    page: a dict with an int timestamp `created`, a str `description` and a
    base32 `secret` of at least 32 chars.
    """

    return (
        isinstance(entry, dict)
        and set(entry) == {'created', 'description', 'secret'}
        and isinstance(entry['created'], int)
        and isinstance(entry['description'], str)
        and isinstance(entry['secret'], str)
        and re.fullmatch(r'[A-Z2-7]{32,}', entry['secret']) is not None
    )

class TOTP:
    def __init__(self, user, secret):
        self.user = user
        self.totp = pyotp.TOTP(secret)

    def make_b64qrcode(self):
        url = f'otpauth://totp/{self.user}?secret={self.totp.secret}'
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        buffer = BytesIO()
        img.save(buffer, format='PNG')

        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def verify(self, code):
        return self.totp.verify(code)