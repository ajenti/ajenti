from jadi import interface


@interface
class ApiDnsManager():
    """
    Abstract interface to manage all DNS API providers.
    """

    id = None
    name = None

    def get_domains(self):
        """
        List all domains managed by the dns api.

        :return: List of domains
        :rtype: list
        """

        raise NotImplementedError

    def get_records(self, domain):
        """
        List all records from a given domain.

        :param domain: the domain, like example.com
        :type domain: basestring
        :return: List of records with details (TTL, name, type, etc...)
        :rtype: list
        """

        raise NotImplementedError

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

        raise NotImplementedError

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

        raise NotImplementedError

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

        raise NotImplementedError
