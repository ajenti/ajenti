import smtplib
import ssl
import logging

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
        return f"""Subject: {subject}
From: {self.user}
To: {recipient}

{content}"""

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

notifications = Mail()