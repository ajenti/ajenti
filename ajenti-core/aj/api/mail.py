import os
import smtplib
import ssl
import logging
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aj


class Mail:
    def __init__(self):
        self.enabled = aj.config.data['email'].get('enable', False)

        if self.enabled:
            try:
                self.server = aj.config.data['email']['smtp']['server']
                self.ssl = aj.config.data['email']['smtp']['port']
                self.user = aj.config.data['email']['smtp']['user']
                self.password = aj.config.data['email']['smtp']['password']
                logging.info("Notifications successfully initialized")
            except KeyError:
                logging.error("Failed to initialize notification system, please verify your smtp settings.")
                self.server = None
                self.ssl = None
                self.user = None
                self.password = None

            if self.ssl == "ssl":
                self.sendMail = self._send_ssl
            elif self.ssl == "starttls":
                self.sendMail = self._send_starttls
            else:
                self.sendMail = lambda *args: None
        else:
            self.sendMail = lambda *args: None

    def _prepare_content(self, subject, recipient, content):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.user
        message["To"] = recipient

        html = MIMEText(content['html'], "html")
        text = MIMEText(content['plain'], "plain")

        message.attach(text)
        message.attach(html)
        return message.as_string()

    def _send_starttls(self, subject, recipient, content):
        message = self._prepare_content(subject, recipient, content)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.server, 587) as server:
                server.starttls(context=context)
                server.login(self.user, self.password)
                server.sendmail(self.user, recipient, message)
        except Exception as e:
            logging.error(f"Failed to send email : {e}")

    def _send_ssl(self, subject, recipient, content):
        message = self._prepare_content(subject, recipient, content)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.server, 465, context=context) as server:
                server.login(self.user, self.password)
                server.sendmail(self.user, recipient, message)
        except Exception as e:
            logging.error(f"Failed to send email : {e}")

    def send_password_reset(self, recipient, link):
        subject = _("Password reset request from ajenti")
        content = {'plain':'', 'html':''}

        # TODO : make it configurable
        static_path = os.path.dirname(__file__) + '/../static'
        html_template = static_path + '/emails/reset_email.html'
        plain_template = static_path + '/emails/reset_email.txt'
        logo_path = static_path + '/images/Logo.png'

        with open(logo_path, "rb") as image:
            base64_logo = base64.b64encode(image.read()).decode()

        with open(plain_template, 'r') as p:
            plain = p.read()
            plain = plain.replace('{{RESET_LINK}}', link)

        with open(html_template, 'r') as h:
            html = h.read()
            html = html.replace('{{BASE64_LOGO}}', base64_logo)
            html = html.replace('{{RESET_LINK}}', link)

        content['html'] = html
        content['plain'] = plain
        self.sendMail(subject, recipient, content)
