import requests
import json
import logging

from jadi import component
from aj.plugins.dns_api.api import ApiDnsManager
from aj.plugins.dns_api.record import Record
import aj

@component(ApiDnsManager)
class GandiApiDnsProvider(ApiDnsManager):
    """
    LiveDNS API for domains hosted by Gandi.
    Full documentation available here: https://api.gandi.net/docs/livedns/
    """

    id = 'gandi'
    name = 'Gandi DNS API'

    def __init__(self, context):
        self.baseUrl = 'https://api.gandi.net/v5/livedns/domains'

    def _req(self, method, apiurl="", data=None):
        """
        Do the request to the api url.

        :param method: get, put, post or delete
        :type method: basestring
        :param apiurl: called url
        :type apiurl: basestring
        :param data: optional data to send (e.g. post)
        :type data: dict
        :return: response from the api
        :rtype: json
        """

        apikey = aj.config.data.get('dns_api', {}).get('apikey', None)
        sharing_id = aj.config.data.get('dns_api', {}).get('sharing_id', None)
        params = {'sharing_id': sharing_id}

        if method not in ["get", "put", "post", "delete"] or apikey is None:
            return

        func = getattr(requests, method)
        if data is None:
            resp = func(
                f"{self.baseUrl}{apiurl}",
                params=params,
                headers={"Authorization": f"Apikey {apikey}"}
            )
        else:
            resp = func(
                f"{self.baseUrl}{apiurl}",
                data=data,
                params=params,
                headers={"Authorization": f"Apikey {apikey}"}
            )

        return resp

    def get_domains(self):
        """
        List all domains managed by livedns under the provided apikey.
        :return: List of domains
        :rtype: list
        """

        domains = json.loads(self._req("get").content)
        return [domain['fqdn'] for domain in domains]

    def get_records(self, domain):
        """
        List all records from a given domain.

        :param domain: the domain, like example.com
        :type domain: basestring
        :return: List of records with details (TTL, name, type, etc...)
        :rtype: list
        """

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
        """
        Add a new record to a given domain.

        :param fqdn: the domain, like example.com
        :type fqdn: basestring
        :param record: the record to add, with all details (TTL, name, type, etc...)
        :type record: Record object
        :return: status of the request and message
        :rtype: tuple
        """

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
        """
        Update a record from a given domain with new values.

        :param fqdn: the domain, like example.com
        :type fqdn: basestring
        :param record: the record to add, with all details (TTL, name, type, etc...)
        :type record: Record object
        :return: status of the request and message
        :rtype: tuple
        """

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

    def delete_record(self, fqdn, rtype, name):
        """
        Delete a record from a given domain.

        :param fqdn: the domain, like example.com
        :type fqdn: basestring
        :param rtype: type of the DNS entry, like CNAME or AAAA
        :type rtype: basestring
        :param name: the record name, like test (to delete the entry test.example.com)
        :type name: basestring
        :return: status of the request and message
        :rtype: tuple
        """

        try:
            resp = self._req('delete', apiurl=f"/{fqdn}/records/{name}/{rtype}")
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