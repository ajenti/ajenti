from aj.plugins.dns_api.api import ApiDnsManager
import aj

class Domain:
    """Basic class for a DNS entry within a given fqdn."""

    def __init__(self, fqdn, manager):
        """

        :param fqdn: the domain, e.g. like exmaple.com
        :type fqdn: basestring
        :param manager: the domain manager instance
        :type manager: DomainManager
        """

        self.fqdn = fqdn
        self.mgr = manager
        self.api = manager.api_provider
        self.records = []

    def get_records(self):
        """
        List all records from self.fqdn.

        :return: List of records with details (TTL, name, type, etc...)
        :rtype: list
        """

        self.api.get_records(self)

    def add_record(self, record):
        """
        Add a new record to self.fqdn.

        :param record: the record to add, with all details (TTL, name, type, etc...)
        :type record: Record object
        :return: status of the request and message
        :rtype: tuple
        """

        return self.api.add_record(self.fqdn, record)

    def update_record(self, record):
        """
        Update a record from self.fqdn with new values.

        :param record: the record to add, with all details (TTL, name, type, etc...)
        :type record: Record object
        :return: status of the request and message
        :rtype: tuple
        """

        return self.api.update_record(self.fqdn, record)

    def delete_record(self, rtype, name):
        """
        Delete a record from self.fqdn.

        :param rtype: type of the DNS entry, like CNAME or AAAA
        :type rtype: basestring
        :param name: the record name, like test (to delete the entry test.example.com)
        :type name: basestring
        :return: status of the request and message
        :rtype: tuple
        """

        return self.api.delete_record(self.fqdn, rtype, name)


class DomainManager:
    """
    Select the configured provider, provide an access to the api and manage
    all domains objects.
    """

    def __init__(self, context):
        self.context = context
        # gandi is currently the only provider
        provider_id = aj.config.data.get('dns_api', {}).get('provider', 'gandi')

        for provider in ApiDnsManager.all(self.context):
            if provider.id == provider_id:
                self.api_provider = provider
                break
        self.domains = {}

    def load(self):
        for domain in self.api_provider.get_domains():
            self.domains[domain] = Domain(domain, self)
