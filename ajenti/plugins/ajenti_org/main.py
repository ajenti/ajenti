import gevent
import requests
import json

from ajenti.api.sensors import Sensor
import ajenti


ENDPOINT = 'http://ajenti.local.org:8080/docking-bay/receive/%i'
ENDPOINT = None

def worker():
    if not ENDPOINT:
        return
    while True:
        datapack = {'sensors': {}}

        for sensor in Sensor.get_all():
            data = {}
            for variant in sensor.get_variants():
                data[variant] = sensor.value(variant)
            datapack['sensors'][sensor.id] = data

        gevent.sleep(3)
        url = ENDPOINT % ajenti.config.tree.installation_id

        try:
            requests.post(url, data={'data': json.dumps(datapack)})
        except:
            pass


gevent.spawn(worker)
