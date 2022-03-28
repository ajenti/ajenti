.. _configuring:


Configuration files
*******************

All the configuration files are store in ``/etc/ajenti`` :

  * config.yml : the main configuration file with all important parameters,
  * smtp.yml : credentials to an email server relay, if you want to use some mail notifications or reset password functionality,
  * users.yml : the default file which contains user account for the user authentication provider.

All configuration files use the `yaml format <https://en.wikipedia.org/wiki/YAML>`

config.yml in details
=====================

Ajenti will use the following parameters :

  * auth:
     *   allow_sudo: **true** or **false** ( allow users in the sudo group to elevate )
     *   emails: {} ( not currently used )
     *   provider: authentication method to use, **os** (users from the os) or **users**
     *   users_file: if the users authentication provider is used, path to the users file (default **/etc/ajenti/users.yml**)
  * bind:
     *   host: ip on which to listen (default **0.0.0.0**)
     *   mode: type of socket, **tcp** or **unix**
     *   port: port on which to listen, default **8000**
  * color: secundary color of the CSS theme (possibles values are **default**, **bluegrey**, **red**, **deeporange**, **orange**, **green**, **teal**, **blue** and **purple**)
  * email:
     *   enable: **true** or **false**, if you want to enable the password reset function. But for this you need to set the smtp credentials in ``/etc/ajenti/smtp.yml``
     *   templates:
        * reset_email : full path to template email for reset password functionality
  * language: language prefence for all users, default **en**
  * logo: full path to your own logo, default is the one from Ajenti
  * max_sessions: max number of simultaneously sessions, default is **99**. If the max is reached, the older inactive session will be deactivated
  * name: your domain name
  * restricted_user: user to use for the restricted functionalities, like for the login page. It's an important security parameter in order to limit the actions in restricted environments : all actions in restricted environments will be done with this user's privileges. Default is **nobody**.
  * session_max_time: max validity time in seconds before automatic logout. Default is **3600** (one hour).
  * ssl:
     *   enable: true
     *   certificate: full path to default global certificate, used to generate client certificates, and fot the https protocol, if the parameter ``fqdn_certificate`` is not set. The PEM file should contains the certificate itself, and the private key.
     *   fqdn_certificate: full path certificate for your FQDN (e.g. ``/etc/ajenti/mycert.pem``). The PEM file should contains the certificate itself, and the private key.
     *   client_auth:
        *     enable: **true** or **false** to enable client authentication via certificates
        *     force: if **true**, only allows login with client certificate. If **false**, also permit authentication with password
        *     certificates: this entry contains all client certifcates for an automatic login. It will be filled through the settings in Ajenti with the following structure:
        *     - digest:
        *       name:
        *       serial:
        *       user:


smtp.yml in details
===================

This file contains all the credentials of an email server which can be used as email relay to send some notifications, like an email to reset a forgotten password.

  * smtp:
     * port: **starttls** (will use 587) or **ssl** (will use 465)
     * server: server hostname, like ``mail.mydomain.com``
     * user: user to authenticate
     * password: password of the mail user

users.yml in details
====================

Ajenti give the possibility to use two authentication methods : **os** or **users**. If **users** is used, all user informations are stored in **users_file**. It's automatically filled with the user plugin.
The default path for the **users_file** is ``/etc/ajenti/users.yml`` with following structure:

  * users:
    * `username`:
      * password: hash of the password
      * permissions: list of permissions of the user
      * uid: related os uid to run the worker on
      * fs_root: root directory
      * email: email to use for password reset.  
