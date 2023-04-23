import requests
import json

from jadi import component
from aj.plugins.dns_api.api import ApiDnsManager
from aj.plugins.dns_api.record import Record
import aj

@component(ApiDnsManager)
class GandiApiDnsProvider(ApiDnsManager):
    id = 'gandi'
    name = 'Gandi DNS API'

    def __init__(self, context):
        apikey = aj.config.data.get('dns_apikey', '') # TODO : wrong config entry for this
        self.baseUrl = 'https://api.gandi.net/v5/livedns/domains'
        self.headers = {"Authorization": f"Apikey {apikey}"}

    def _req(self, method, apiurl="", data=None):
        if method not in ["get", "put", "post", "delete"]:
            return

        func = getattr(requests, method)
        if data is None:
            resp = func(f"{self.baseUrl}{apiurl}", headers=self.headers)
        else:
            resp = func(f"{self.baseUrl}{apiurl}", data=data, headers=self.headers)

        return resp

    def get_domains(self):
        domains = json.loads(self._req("get").content)
        return [domain['fqdn'] for domain in domains]

    def get_records(self, domain):
        resp = self._req('get', apiurl=f"/{domain.fqdn}/records")
        records = json.loads(resp.content)

        for record in sorted(records, key=lambda d: d['rrset_name']):
            domain.records.append(Record(
                domain.fqdn,
                record['rrset_name'],
                record['rrset_ttl'],
                record['rrset_type'],
                record['rrset_values'])
            )