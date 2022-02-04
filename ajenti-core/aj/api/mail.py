import os
import smtplib
import ssl
import logging
import base64
from bs4 import BeautifulSoup
from jinja2 import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aj

DEFAULT_TEMPLATES = {
    'reset_email': os.path.dirname(__file__) + '/../static/emails/reset_email.html',
}

class Mail:
    def __init__(self):
        self.enabled = aj.config.data['email'].get('enable', False)

        if self.enabled:
            try:
                self.server = aj.smtp_config.data['smtp']['server']
                self.ssl = aj.smtp_config.data['smtp']['port']
                self.user = aj.smtp_config.data['smtp']['user']
                logging.info("Notifications successfully initialized")
            except KeyError:
                logging.error("Failed to initialize notification system, please verify your smtp settings.")
                self.server = None
                self.ssl = None
                self.user = None

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
                server.login(self.user, aj.smtp_config.get_smtp_password())
                server.sendmail(self.user, recipient, message)
        except Exception as e:
            logging.error(f"Failed to send email : {e}")

    def _send_ssl(self, subject, recipient, content):
        message = self._prepare_content(subject, recipient, content)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.server, 465, context=context) as server:
                server.login(self.user, aj.smtp_config.get_smtp_password())
                server.sendmail(self.user, recipient, message)
        except Exception as e:
            logging.error(f"Failed to send email : {e}")

    def get_template(self, template):
        """
        Check if a template is configured in aj config files and use it.
        If not, fallback to the entry in DEFAULT_TEMPLATES, i.e.
        default templates in Ajenti.

        :param template: Name of the template
        :type template: basestring
        :return: Path of template to use
        :rtype: basestring
        """

        template_path = aj.config.data['email']['templates'].get(template, 'default')

        if template_path == 'default' or not os.path.isfile(template_path):
            template_path = DEFAULT_TEMPLATES[template]

        return template_path

    def render_template(self, template_path, vars=None):
        """
        Use Jinja2 template engine to render the HTML template.
        Use BeautifulSoup to generate the plain text content with the html content.

        :param template_path: Path to the HTML template
        :type template_path: basestring
        :param vars: All var to render with Jinja2
        :type vars: dict
        :return: HTML and plain text content to send per email
        :rtype: dict
        """

        content = {'plain':'', 'html':''}

        with open(template_path, 'r') as h:
            template = Template(h.read())
            html = template.render(vars)

            soup = BeautifulSoup(html, "html.parser")

        # Generating plain text source from html source
        # The style tag and .link_button are removed
        for style in soup.select('style,.link_button'):
            style.extract()

        # Only keep the text inside the tags
        plain = ''.join(soup.findAll(text=True)).strip()

        content['html'] = html
        content['plain'] = plain

        return content

    def send_password_reset(self, recipient, link):
        subject = _("Password reset request from ajenti")
        html_template = self.get_template('reset_email')
        logo_path = aj.config.data['logo']

        with open(logo_path, "rb") as image:
            base64_logo = base64.b64encode(image.read()).decode()

        vars = {
            'BASE64_LOGO': base64_logo,
            'RESET_LINK': link,
        }

        content = self.render_template(html_template, vars)

        self.sendMail(subject, recipient, content)
