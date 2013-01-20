"""
Module for sending usage statistics to ajenti.org
"""

import ajenti
import requests
import gevent
import logging

from ajenti.util import *


HOST = 'meta.ajenti.org'
URL = 'http://%s/api/v2/' % HOST


enabled = True


@public
def start():
    gevent.spawn(worker)


def send(url, data):
    id = ajenti.config.tree.installation_id
    if id:
        data['id'] = id
    logging.debug('Feedback >> %s (%s)' % (url, data))
    response = requests.post(URL + url, data=data)
    logging.debug('Feedback << %s' % response.text)
    return response.json()


@public
def send_feedback(email, text):
    send('feedback', {'email': email, 'text': text})


def worker():
    global enabled
    enabled = ajenti.config.tree.enable_feedback
    if enabled:
        if not ajenti.config.tree.installation_id:
            logging.debug('Registering installation')
            enabled = False
            try:
                data = {
                    'version': ajenti.version,
                    'os': ajenti.platform,
                }
                resp = send('register', data)
                if resp['status'] != 'ok':
                    return
            except:
                return
            ajenti.config.tree.installation_id = resp['id']
            ajenti.config.save()
            enabled = True

        while True:
            send('ping', {})
            gevent.sleep(3600 * 12)
