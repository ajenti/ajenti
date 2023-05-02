import qrcode
import pyotp
import base64
from io import BytesIO

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