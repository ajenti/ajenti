.. _plugin_network:

Plugin network
**************

This plugin contains the utilities to show the most important informations about your network interfaces.

.. image:: ../../img/rd-network.png

Tab network
===========

You will see all network interfaces, their IP and status. It's possible to bring an interface up or down and change some of their properties (not yet implemented for systems running with ``netplan``).
It's also possible to update the hostname name.

Tab DNS
=======

This tab enable DNS management (add or delete DNS server).

Tab Hosts
=========

Lists all entries in the file ``/etc/hosts``, and modify or delete any single of them.

