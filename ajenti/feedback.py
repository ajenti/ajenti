"""
Module for sending usage statistics to ajenti.org
"""

import ajenti
import requests
import json
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
    try:
        response = requests.post(URL + url, data=data)
    except:
        raise IOError()
    logging.debug('Feedback << %s' % response.content)
    return json.loads(response.content)


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
                    'edition': ajenti.edition,
                }
                resp = send('register', data)
                if resp['status'] != 'ok':
                    return
            except IOError:
                pass
            ajenti.config.tree.installation_id = resp['id']
            ajenti.config.save()
            enabled = True

        while True:
            try:
                send('ping', {})
            except IOError:
                pass
            gevent.sleep(3600 * 12)
