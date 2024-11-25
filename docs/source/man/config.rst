.. _configuring:


Configuration files
*******************

All the configuration files are store in ``/etc/ajenti`` :

  * **config.yml**: the main configuration file with all important parameters,
  * **smtp.yml**: credentials for an email server relay, used for reset password functionality,
  * **users.yml**: the default file which contains user account for the user authentication provider.

All configuration files use the `yaml format <https://en.wikipedia.org/wiki/YAML>`_

config.yml in details
=====================

Ajenti will use the following parameters :

auth block
----------

.. code-block:: yaml

    auth:
      allow_sudo: true
      emails: {}
      provider: os
      users_file: /etc/ajenti/users.yml

Explanations:

  * **allow_sudo**: **true** or **false** (allow users in the sudo group to elevate)
  * **emails**: {} (not currently used)
  * **provider**: authentication method to use, **os** (users from the os) or **users**
  * **users_file**: if the users authentication provider is used, path to the users file (default **/etc/ajenti/users.yml**)

The parameter **user_config** was used to specified where the user configuration was stored, but is now deprecated, since it's bound to the **provider** (**os** or **users**) to avoid duplicates entries.

bind block
----------

.. code-block:: yaml

    bind:
      host: 0.0.0.0
      mode: tcp
      port: 8000

Explanations:

  * **host**: ip on which to listen (default **0.0.0.0**)
  * **mode**: type of socket, **tcp** or **unix**
  * **port**: port on which to listen, default **8000**

ssl block
---------

.. code-block:: yaml

    ssl:
      enable: true
      certificate: /etc/ajenti/mycert.pem
      fqdn_certificate: /etc/letsencrypt/ajenti.pem
      force: false
      client_auth:
         enable: true
         force: true
         certificates:
           digest: 15:E8:5E:E5:D2:E8:75:0D:53:FF:22:A8:79:28:E5:BE:33:E0:37:07:FB:31:47:4D:61:69:AB:43:F8:5B:23:78
           name: C=NA,ST=NA,O=sajenti.mydomain.com,CN=root@ajenti.mydomain.com
           serial: 352674123960898230347891590646542168839110009016
           user: root

Explanations:

  * **enable**: **true** or **false** to provide support for https. It's highly recommended to set it to **true**
  * **certificate**: full path to default global certificate, used to generate client certificates, and fot the https protocol, if the parameter ``fqdn_certificate`` is not set. The PEM file should contains the certificate itself, and the private key.
  * **fqdn_certificate**: full path certificate for your FQDN (e.g. ``/etc/ajenti/mycert.pem``). The PEM file should contains the certificate itself, and the private key.
  * **force**: spawn a small listener on port 80 to enable a redirect from ``http://hostname`` to ``https://hostname:port``.
  * **client_auth**:
     * **enable**: **true** or **false** to enable client authentication via certificates
     * **force**: if **true**, only allows login with client certificate. If **false**, also permit authentication with password
     * **certificates**: this entry contains all client certifcates for an automatic login. It will be filled through the settings in Ajenti with the following structure:
        * **digest**: digest of the certificate
        * **name**: name of the certificate
        * **serial**: serial of the certificate
        * **user**: username

email block
-----------

.. code-block:: yaml

    email:
      enable: true
      templates:
        reset_email : /etc/ajenti/email/mytemplate_for_reset_password.html

Explanations:

  * **enable**: **true** or **false**, if you want to enable the password reset function. But for this you need to set the smtp credentials in ``/etc/ajenti/smtp.yml``
  * **templates**:
    * **reset_email**: full path to template email for reset password functionality

The default template used to reset email password is located `here <https://github.com/ajenti/ajenti/blob/master/ajenti-core/aj/static/emails/reset_email.html>`_.
The variables are automatically filled with jinja2.

Other global parameters
-----------------------

.. code-block:: yaml

    color: blue
    language: en
    logo: /srv/dev/ajenti/ajenti-panel/aj/static/images/Logo.png
    max_sessions: 10
    name: ajenti.mydomain.com
    restricted_user: nobody
    session_max_time: 1200

Explanations:

  * **color**: secundary color of the CSS theme (possibles values are **default**, **bluegrey**, **red**, **deeporange**, **orange**, **green**, **teal**, **blue** and **purple**)
  * **language**: language prefence for all users, default **en**
  * **logo**: full path to your own logo, default is `the one from Ajenti <https://github.com/ajenti/ajenti/blob/master/ajenti-core/aj/static/images/Logo.png>`_
  * **max_sessions**: max number of simultaneously sessions, default is **99**. If the max is reached, the older inactive session will be deactivated
  * **name**: your domain name
  * **restricted_user**: user to use for the restricted functionalities, like for the login page. It's an important security parameter in order to limit the actions in restricted environments : all actions in restricted environments will be done with this user's privileges.
    Default is **nobody**.
  * **session_max_time**: max validity time in seconds before automatic logout.
    Default is **3600** (one hour).
  * **trusted_domains** ( `Ajenti` >= 2.2.1 ) : comma separated list of trusted domains under which it's possible to reach your `Ajenti` server. When the HTTP headers are tested, a valid origin will be considered as one of the domains listed. It's necessary to specify the protocol and the port. It's mean that an entry should look like `http://my.domain.com:8000`. If set, the first entry of this list will be used as url for the password reset functionality, for more security.
  * **trusted_proxies** ( `Ajenti` >= 2.2.1 ) : comma separated list of trusted proxies. This is actually used in order to get the real ip of the client.

smtp.yml in details
===================

This file contains all the credentials of an email server which can be used as email relay to send an email to reset a forgotten password. A mail backend is prepared in ajenti-core, and this could be possibly be used in the future to send some other notifications, but it's currently only used in order to reset a password.

.. code-block:: yaml

    smtp:
      password: MyVeryStrongStrongPassword
      port: starttls
      server: mail.mydomain.com
      user: mail@mydomain.com

Explanations:

     * **port**: **starttls** (will use 587) or **ssl** (will use 465)
     * **server**: server hostname, like ``mail.mydomain.com``
     * **user**: user to authenticate
     * **password**: password of the mail user

users.yml in details
====================

Ajenti gives the possibility to use two authentication methods : **os** or **users**. If **users** is used, all user informations are stored in **users_file**. It's automatically filled with the user plugin.


The default path for the **users_file** is ``/etc/ajenti/users.yml`` with following structure:

.. code-block:: yaml

    users:
      arnaud:
        email: arnaud@mydomain.com
        fs_root: /home/arnaud
        password: 73637279707.....
        permissions:
          packages:install: false
          sidebar:view:/view/cron: false
        uid: 1002

Explanations:

  * **password**: hash of the password (see :ref:`how_to_generate_password_hash`)
  * **permissions**: list of permissions of the user
  * **uid**: related os uid to run the worker on
  * **fs_root**: root directory
  * **email**: email to use for password reset.

.. _how_to_generate_password_hash:

how to generate password hash
=============================
Ajenti uses ``scrypt`` for encryption and hashing.

To "hash" your desired password with scrypt, you can do the following:

.. code-block:: py

  import scrypt, os
  
  bytes = scrypt.encrypt(os.urandom(256), "password", maxtime=1)
  hex = bytes.hex()
  print(hex)

Note that ``scrypt.encrypt`` doesn't produce a traditional hash. It produces a derived key.
