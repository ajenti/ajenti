import requests
import json
import logging

from jadi import component
from aj.plugins.dns_api.api import ApiDnsManager
from aj.plugins.dns_api.record import Record
import aj

@component(ApiDnsManager)
class GandiApiDnsProvider(ApiDnsManager):
    id = 'gandi'
    name = 'Gandi DNS API'

    def __init__(self, context):
        self.baseUrl = 'https://api.gandi.net/v5/livedns/domains'

    def _req(self, method, apiurl="", data=None):
        apikey = aj.config.data.get('dns_api', {}).get('apikey', None)

        if method not in ["get", "put", "post", "delete"] or apikey is None:
            return

        func = getattr(requests, method)
        if data is None:
            resp = func(
                f"{self.baseUrl}{apiurl}",
                headers={"Authorization": f"Apikey {apikey}"}
            )
        else:
            resp = func(
                f"{self.baseUrl}{apiurl}",
                data=data,
                headers={"Authorization": f"Apikey {apikey}"}
            )

        return resp

    def get_domains(self):
        domains = json.loads(self._req("get").content)
        return [domain['fqdn'] for domain in domains]

    def get_records(self, domain):
        resp = self._req('get', apiurl=f"/{domain.fqdn}/records")
        records = json.loads(resp.content)
        domain.records = []

        for record in sorted(records, key=lambda d: d['rrset_name']):
            domain.records.append(Record(
                record['rrset_name'],
                record['rrset_ttl'],
                record['rrset_type'],
                record['rrset_values'])
            )

    def add_record(self, fqdn, record):
        try:
            data = json.dumps({
                'rrset_name': record.name,
                'rrset_type': record.type,
                'rrset_values': record.values,
                'rrset_ttl': record.ttl
            })
            resp = self._req('post', apiurl=f"/{fqdn}/records", data=data)
            messages = json.loads(resp.content)
            if messages.get('status', '') == 'error':
                return resp.status_code, messages['errors']
            else:
                return resp.status_code, messages['message']
        except Exception as e:
            logging.error(e)

    def update_record(self, fqdn, record):
        try:
            data = json.dumps({'items': [{
                'rrset_name': record.name,
                'rrset_type': record.type,
                'rrset_values': record.values,
                'rrset_ttl': record.ttl
            }]})
            resp = self._req('put', apiurl=f"/{fqdn}/records/{record.name}", data=data)
            messages = json.loads(resp.content)
            if messages.get('status', '') == 'error':
                return resp.status_code, messages['errors']
            else:
                return resp.status_code, messages['message']
        except Exception as e:
            logging.error(e)

    def delete_record(self, fqdn, name):
        try:
            resp = self._req('delete', apiurl=f"/{fqdn}/records/{name}")
            if resp.content:
                messages = json.loads(resp.content)
            else:
                messages = {'message': 'Entry deleted'}
            if messages.get('status', '') == 'error':
                return resp.status_code, messages['errors'][0]['description']
            else:
                return resp.status_code, messages['message']
        except Exception as e:
            logging.error(e)