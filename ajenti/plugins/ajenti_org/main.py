import gevent
import requests

import ajenti


ENDPOINT = 'http://ajenti.local.org:8080/docking-bay/receive/%i'


def worker():
    while True:
        gevent.sleep(3)
        url = ENDPOINT % ajenti.config.tree.installation_id
        requests.post(url)


gevent.spawn(worker)
