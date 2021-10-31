.. _security:


Securing
********


Fail2ban
========

Failed login attempts are logged in `/var/log/ajenti/ajenti.log`. A basic filter for Fail2ban is available here : https://raw.githubusercontent.com/ajenti/ajenti/master/scripts/ajenti.conf


You can enable it by copying it in `/etc/fail2ban/filter.d/ajenti.conf` and with the following lines in `/etc/fail2ban/jail.d/ajenti` :

::

    [ajenti]
    enabled = true
    port    = 8000
    bantime = 120
    maxretry = 3
    findtime = 60
    logpath = /var/log/ajenti/ajenti.log
    filter = ajenti

This is only an example : after 3 failed attempts ( `maxretry` ) the last 60 seconds ( `findtime` ), the found ip will be banned 2 minutes ( `bantime` ). You can naturally set other values related to your configuration.
