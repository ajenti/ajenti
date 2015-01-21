from aj.util import LazyModule
requests = LazyModule('requests')

import crypt
import json
import logging
import os
import pwd
import spwd
import subprocess

import aj
import aj.pam
from aj.api import *
from aj.api.http import BaseHttpHandler
from aj.util import *


class SudoError (Exception):
    def __init__(self, message):
        self.message = message


@public
@service
class AuthenticationMiddleware (BaseHttpHandler):
    def __init__(self, context):
        self.context = context
        self.auth = AuthenticationService.get(self.context)
        if not hasattr(context, 'identity'):
            context.identity = None

    def handle(self, http_context):
        if http_context.env['SSL_VALID']:
            if not self.context.identity:
                cn = http_context.env['SSL_CN']
                if '@' in cn:
                    username = cn.split('@')[0]
                    try:
                        pwd.getpwnam(username)
                        found = True
                    except KeyError:
                        found = False
                    if found:
                        self.auth.login(username)

        http_context.add_header('X-Auth-Identity', str(self.context.identity or ''))


@public
@service
class AuthenticationService (BaseHttpHandler):
    def __init__(self, context):
        self.context = context
        if os.geteuid() != 0:
            username = pwd.getpwuid(os.geteuid()).pw_name
            self.login(username, demote=False)

    def check_password(self, username, password):
        try:
            enc_pwd = spwd.getspnam(username)[1]

            if enc_pwd in ["NP", "!", "", None]:
                return "user '%s' has no password set" % user
            if enc_pwd in ["LK", "*"]:
                return "account is locked"
            if enc_pwd == "!!":
                return "password has expired"

            if crypt.crypt(password, enc_pwd) == enc_pwd:
                return True
            else:
                return False
        except KeyError:
            return False
        return False

    def check_sudo_password(self, username, password):
        sudo = subprocess.Popen(
            ['sudo', '-S', '-u', 'eugene', '--', 'sh', '-c', 'sudo -k; sudo -S echo'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        o, e = sudo.communicate(password + '\n')
        if sudo.returncode != 0:
            raise SudoError((o + e).splitlines()[-1].strip())
        return True

    def check_persona_assertion(self, assertion, audience):
        params = {
            'assertion': assertion,
            'audience': audience,
        }

        resp = requests.post('https://verifier.login.persona.org/verify', data=params, verify=True)

        if resp.ok:
            verification_data = json.loads(resp.content)
            if verification_data['status'] == 'okay':
                email = verification_data['email']
                return email
            else:
                raise Exception('Persona auth failed')
        else:
            raise Exception('Request failed')

    def check_client_certificate(self, connection, x509, e1, e2, e3):
        print 'verifying cert', connection, x509
        return True

    def get_identity(self):
        return self.context.identity

    def login(self, username, demote=True):
        logging.info('Authenticating session as %s' % username)
        if demote:
            self.context.worker.demote(username)
        self.context.identity = username
