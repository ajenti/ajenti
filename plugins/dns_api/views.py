from jadi import component
from dataclasses import asdict

from aj.api.http import get, put, post, delete, HttpPlugin
from aj.auth import authorize
from aj.plugins.dns_api.record import Record
from aj.api.endpoint import endpoint, EndpointError
from aj.plugins.dns_api.manager import DomainManager


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.mgr = DomainManager(self.context)

    @get(r'/api/dns_api/domains')
    @endpoint(api=True)
    def handle_api_dns_list_domains(self, http_context):
        """
        List all available domains.

        :return: list of domains and provider name
        :rtype: tuple
        """
        self.mgr.load()
        return list(self.mgr.domains.keys()), self.mgr.api_provider.name

    @get(r'/api/dns_api/domain/(?P<fqdn>[\w\.]+)/records')
    @endpoint(api=True)
    def handle_api_dns_list_records(self, http_context, fqdn):
        """
        List records from a given domain.

        :param fqdn: the domain, like example.com
        :type fqdn: basestring
        :return: list of dict, one dict per record
        :rtype: list
        """

        self.mgr.domains[fqdn].get_records()
        return [asdict(r) for r in self.mgr.domains[fqdn].records]

    @post(r'/api/dns_api/domain/(?P<fqdn>[\w\.]+)/records/(?P<name>.*)')
    @endpoint(api=True)
    def handle_api_dns_post_record(self, http_context, fqdn, name):
        """
        Add a record to a domain.

        :param fqdn: the domain, like example.com
        :type fqdn: basestring
        :param name: name of the record
        :type name: basestring
        :return: Status of the request
        :rtype: tuple
        """

        record = Record (
            name,
            http_context.json_body()['ttl'],
            http_context.json_body()['type'],
            [http_context.json_body()['values']]
        )
        return self.mgr.domains[fqdn].add_record(record)

    @put(r'/api/dns_api/domain/(?P<fqdn>[\w\.]+)/records/(?P<name>.*)')
    @endpoint(api=True)
    def handle_api_dns_put_record(self, http_context, fqdn, name):
        """
        Update a record to a domain.

        :param fqdn: the domain, like example.com
        :type fqdn: basestring
        :param name: name of the record
        :type name: basestring
        :return: Status of the request
        :rtype: tuple
        """

        record = Record (
            name,
            http_context.json_body()['ttl'],
            http_context.json_body()['type'],
            [http_context.json_body()['values']]
        )
        return self.mgr.domains[fqdn].update_record(record)

    @delete(r'/api/dns_api/domain/(?P<fqdn>[\w\.]+)/records/(?P<rtype>[A-Z]*)/(?P<name>.*)')
    @endpoint(api=True)
    def handle_api_dns_delete_record(self, http_context, fqdn, rtype, name):
        """
        Delete a record to a domain.

        :param fqdn: the domain, like example.com
        :type fqdn: basestring
        :param rtype: the DNS type, like AAAA, to avoid deleting all entries
        with given name
        :type rtype: basestring
        :param name: name of the record
        :type name: basestring
        :return: Status of the request
        :rtype: tuple
        """

        return self.mgr.domains[fqdn].delete_record(rtype, name)